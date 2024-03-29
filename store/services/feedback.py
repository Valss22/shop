from rest_framework import status
from store.serializers import *
from store.models import *
from rest_framework.response import Response


def add_feedback(self, request, pk):
    access = self.request.headers['Authorization'].split(' ')[1]
    access = parse_id_token(access)
    current_user = User.objects.get(email=access['email'])

    Feedback.objects.create(
        user=current_user,
        username=User.objects.get(email=access['email']).username,
        comment=request.data['comment']
    )
    current_feedback = Feedback.objects.filter(user=current_user).last()
    Product.objects.get(id=pk).comments.add(current_feedback)

    responce = Response()
    responce.data = {
        'id': current_feedback.id,
        'comment': current_feedback.comment,
        'username': current_feedback.username,
        'date': current_feedback.date
    }
    return responce


def set_like(current_user: User, pk: int, case: bool) -> Response:
    FeedbackRelation.objects.filter(
        user=current_user,
        comment_id=pk).update(
        like=not case
    )
    if not case:
        FeedbackRelation.objects.filter(
            user=current_user,
            comment_id=pk).update(
            dislike=case
        )
    if case:
        like_count = FeedbackRelation.objects.filter(
            comment_id=pk,
            like=case).count(
        )
        dislikeCount = FeedbackRelation.objects.filter(
            comment_id=pk,
            dislike=case).count(
        )
    else:
        like_count = FeedbackRelation.objects.filter(
            comment_id=pk,
            like=not case).count(
        )
        dislikeCount = FeedbackRelation.objects.filter(
            comment_id=pk,
            dislike=not case).count(
        )

    responce = Response()
    responce.data = {
        'isLiked': not case,
        'likeCount': like_count,
        'dislikeCount': dislikeCount,
    }
    if not case:
        responce.data['isDisliked'] = False
    return responce


def rate_feedback(self, request, set_like, pk):
    access = self.request.headers['Authorization'].split(' ')[1]
    access = parse_id_token(access)
    current_user = User.objects.get(email=access['email'])
    FeedbackRelation.objects.get_or_create(user=current_user, comment_id=pk)
    responce = Response()

    if request.data['data'] == 'like':
        if FeedbackRelation.objects.get(user=current_user, comment_id=pk).like:
            return set_like(current_user, pk, True)
        else:
            return set_like(current_user, pk, False)
    elif request.data['data'] == 'dislike':
        if FeedbackRelation.objects.get(
                user=current_user,
                comment_id=pk).dislike:
            FeedbackRelation.objects.filter(
                user=current_user,
                comment_id=pk).update(
                dislike=False
            )
            like_count = FeedbackRelation.objects.filter(
                comment_id=pk, like=True).count()
            dislike_count = FeedbackRelation.objects.filter(
                comment_id=pk, dislike=True).count()

            responce.data = {
                'isDisliked': False,
                'likeCount': like_count,
                'dislikeCount': dislike_count,
            }
            return responce
        else:
            FeedbackRelation.objects.filter(
                user=current_user,
                comment_id=pk).update(dislike=True)
            FeedbackRelation.objects.filter(
                user=current_user,
                comment_id=pk).update(like=False)

            like_count = FeedbackRelation.objects.filter(
                comment_id=pk, like=True).count()
            dislike_count = FeedbackRelation.objects.filter(
                comment_id=pk, dislike=True).count()

            responce.data = {
                'isLiked': False,
                'isDisliked': True,
                'likeCount': like_count,
                'dislikeCount': dislike_count,
            }
            return responce
    else:
        return Response({'message': 'invalid request body'},
                        status.HTTP_400_BAD_REQUEST)
