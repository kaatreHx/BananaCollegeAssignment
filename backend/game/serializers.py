from rest_framework import serializers


class AnswerSerializer(serializers.Serializer):
    """Body of POST /api/game/answer/."""

    round_id = serializers.CharField()
    answer = serializers.IntegerField(min_value=0, max_value=999)
