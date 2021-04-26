from rest_framework import status
from store.serializers import *
from store.models import *
from rest_framework.response import Response


def add_feedback(self, request, pk):
    access = self.request.headers['Authorization'].split(' ')[1]
    access = parse_id_token(access)
    currentUser = User.objects.get(email=access['email'])

    Feedback.objects.create(
        user=currentUser,
        username=User.objects.get(email=access['email']).username,
        comment=request.data['comment']
    )
    currentFeedback = Feedback.objects.filter(user=currentUser).last()
    Product.objects.get(id=pk).comments.add(currentFeedback)

    responce = Response()
    responce.data = {
        'id': currentFeedback.id,
        'comment': currentFeedback.comment,
        'username': currentFeedback.username,
        'date': currentFeedback.date
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
        likeCount = FeedbackRelation.objects.filter(
            comment_id=pk,
            like=case).count(
        )
        dislikeCount = FeedbackRelation.objects.filter(
            comment_id=pk,
            dislike=case).count(
        )
    else:
        likeCount = FeedbackRelation.objects.filter(
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
        'likeCount': likeCount,
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
            likeCount = FeedbackRelation.objects.filter(
                comment_id=pk, like=True).count()
            dislikeCount = FeedbackRelation.objects.filter(
                comment_id=pk, dislike=True).count()

            responce.data = {
                'isDisliked': False,
                'likeCount': likeCount,
                'dislikeCount': dislikeCount,
            }
            return responce
        else:
            FeedbackRelation.objects.filter(
                user=current_user,
                comment_id=pk).update(dislike=True)
            FeedbackRelation.objects.filter(
                user=current_user,
                comment_id=pk).update(like=False)

            likeCount = FeedbackRelation.objects.filter(
                comment_id=pk, like=True).count()
            dislikeCount = FeedbackRelation.objects.filter(
                comment_id=pk, dislike=True).count()

            responce.data = {
                'isLiked': False,
                'isDisliked': True,
                'likeCount': likeCount,
                'dislikeCount': dislikeCount,
            }
            return responce
    else:
        return Response({'message': 'invalid request body'},
                        status.HTTP_400_BAD_REQUEST)
