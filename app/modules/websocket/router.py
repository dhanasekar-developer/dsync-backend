from uuid import UUID
from fastapi import APIRouter, HTTPException, WebSocket, WebSocketDisconnect, status
from jose import ExpiredSignatureError, JWTError
from app.common.utils import decode_token
from app.modules.websocket.manager import manager
from app.db.database import db_dependency
from app.modules.websocket.service import SocketChatService


router = APIRouter(
    prefix='/ws',
    tags=['WS']
)

socket_service = SocketChatService()

@router.websocket('/')
async def websocket_endpoint(websocket: WebSocket, db: db_dependency):

    token = websocket.query_params.get('token')
    
    user_id = None

    if not token:
        await websocket.close(code=1008, reason='Token not exist!')
        return
    
    try:

        token_data = decode_token(token)

        if token_data['type'] != 'access':
            await websocket.close(code=4002, reason='Invalid token!')
            return
        
        user_id = str(token_data['sub'])

        await manager.connect(user_id, websocket)
        await socket_service.notify_online(UUID(user_id), db)
        
        while True:
            data = await websocket.receive_json()

            if data['type'] == 'ready':
                await socket_service.sync_delivered_message(UUID(user_id), db)
                await socket_service.send_initial_presence(UUID(user_id), db)

                continue

            data = { **data, 'user_id': UUID(user_id)}

            await socket_service.handle_received_message(data, db)

    except WebSocketDisconnect:
        pass

    except ExpiredSignatureError:
        websocket.close(code=4001, reason='Token expired!')

    except JWTError:
        websocket.close(code=4002, reason='Invalid token!')

    except Exception:
        if websocket.client_state.name != 'DISCONNECTED':
            websocket.close(code=1011)

    finally:
        if user_id:
            manager.disconnect(user_id, websocket)
            if not manager.is_online(user_id):
                await socket_service.notify_offline(UUID(user_id), db)


