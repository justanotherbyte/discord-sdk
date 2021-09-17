class InteractionType:
    PING                = 1
    APPLICATION_COMMAND = 2
    MESSAGE_COMPONENT   = 3

class InteractionCallbackType:
    PONG                                 = 1
    CHANNEL_MESSAGE_WITH_SOURCE          = 4
    DEFERRED_CHANNEL_MESSAGE_WITH_SOURCE = 5
    DEFERRED_UPDATE_MESSAGE              = 6
    UPDATE_MESSAGE                       = 7
