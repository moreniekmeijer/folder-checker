from Foundation import NSObject, NSLog
from UserNotifications import (
    UNUserNotificationCenter,
    UNMutableNotificationContent,
    UNNotificationRequest,
    UNTimeIntervalNotificationTrigger,
)


class FCNotificationDelegate(NSObject):
    def userNotificationCenter_didDeliverNotification_(self, center, notification):
        NSLog("Notification delivered: %@", notification)

    def userNotificationCenter_didReceiveNotificationResponse_withCompletionHandler_(
        self, center, response, completionHandler
    ):
        NSLog("Notification clicked: %@", response)
        completionHandler()

_delegate = FCNotificationDelegate.alloc().init()


def setup_notifications(completion_handler):
    center = UNUserNotificationCenter.currentNotificationCenter()
    center.setDelegate_(_delegate)

    options = (1 << 0) | (1 << 2)  # alert + sound

    def completion(granted, error):
        from Foundation import NSLog
        NSLog("Granted: %s" % granted)
        completion_handler(granted)

    center.requestAuthorizationWithOptions_completionHandler_(options, completion)


def send_notification(title, message, delay=0):
    content = UNMutableNotificationContent.alloc().init()
    content.setTitle_(title)
    content.setBody_(message)
    
    trigger = UNTimeIntervalNotificationTrigger.triggerWithTimeInterval_repeats_(max(delay, 0.1), False)
    
    identifier = f"FolderCheckerNotification-{title}"
    
    request = UNNotificationRequest.requestWithIdentifier_content_trigger_(
        identifier, content, trigger
    )
    
    center = UNUserNotificationCenter.currentNotificationCenter()
    center.addNotificationRequest_withCompletionHandler_(request, None)
