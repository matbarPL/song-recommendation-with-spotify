import bson
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask_restful import Resource, reqparse

from models.event import EventModel
from models.user import UserModel


class InvitationByUsername(Resource):
    @classmethod
    @jwt_required
    def post(cls, event_id: str):
        parser = reqparse.RequestParser()
        parser.add_argument('username', type=str, required=True)
        data = parser.parse_args()

        current_userid = get_jwt_identity()
        current_user = UserModel.find_by_id(bson.ObjectId(current_userid))
        if not current_user:
            return {"message": "Current user not found"}, 403

        user_to_add = UserModel.find_by_username(data['username'])
        if not user_to_add:
            return {"message": "User you want to add not found"}, 403

        event = EventModel.find_by_id_and_admin_id(bson.ObjectId(event_id), current_user.id)
        if not event:
            return {"message": "Event with admin as current user not found"}, 403

        if len(list(filter(lambda participant: participant.user_id == user_to_add.id, event.participants))) > 0:
            return {"message": "User you want to add is already in event"}, 403

        is_success = EventModel.add_new_participant(event.id, user_to_add.id)
        if not is_success:
            return {"message": "Some error occured"}, 400

        return {"message": "User joined event successfully"}, 200


class JoinByLink(Resource):
    @classmethod
    @jwt_required
    def get(cls):
        parser = reqparse.RequestParser()
        parser.add_argument('invitation_link', type=str, required=True)
        data = parser.parse_args()

        current_userid = get_jwt_identity()
        current_user = UserModel.find_by_id(bson.ObjectId(current_userid))
        if not current_user:
            return {"message": "User not found"}, 403

        invitation_link = data['invitation_link']
        event = EventModel.find_by_invitation_link(invitation_link)

        if len(list(filter(lambda participant: participant.user_id == current_user.id, event.participants))) > 0:
            return {"message": "User you want to add is already in event"}, 403

        is_success = EventModel.add_new_participant(event.id, current_user.id)
        if not is_success:
            return {"message": "Some error occured"}, 400

        return {"message": "User joined event successfully"}, 200
