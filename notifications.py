import objc
from Foundation import NSObject, NSLog
from UserNotifications import (
    UNUserNotificationCenter,
    UNMutableNotificationContent,
    UNNotificationRequest,
    UNTimeIntervalNotificationTrigger,
)

# --- Delegate class om notificaties af te handelen ---
class FCNotificationDelegate(NSObject):
    def userNotificationCenter_didDeliverNotification_(self, center, notification):
        NSLog("Notification delivered: %@", notification)

    def userNotificationCenter_didReceiveNotificationResponse_withCompletionHandler_(
        self, center, response, completionHandler
    ):
        NSLog("Notification clicked: %@", response)
        completionHandler()

# --- Singleton delegate ---
_delegate = FCNotificationDelegate.alloc().init()

def setup_notifications():
    """
    Installeer de delegate en vraag toestemming voor notificaties.
    Geeft True terug als toestemming verleend is, anders False.
    """
    center = UNUserNotificationCenter.currentNotificationCenter()
    center.setDelegate_(_delegate)

    result = {"granted": False}

    def completion(granted, error):
        from Foundation import NSLog
        NSLog("Granted: %s" % granted)
        result["granted"] = granted

    options = (1 << 0) | (1 << 2)  # alert + sound
    center.requestAuthorizationWithOptions_completionHandler_(options, completion)

    return result

def send_notification(title, message, delay=0):
    """
    Toon een lokale notificatie met title en message.
    delay: tijd in seconden voordat de notificatie verschijnt.
    """
    content = UNMutableNotificationContent.alloc().init()
    content.setTitle_(title)
    content.setBody_(message)
    
    # Trigger instellen
    trigger = UNTimeIntervalNotificationTrigger.triggerWithTimeInterval_repeats_(max(delay, 0.1), False)
    
    # Unieke identifier
    identifier = f"FolderCheckerNotification-{title}"
    
    request = UNNotificationRequest.requestWithIdentifier_content_trigger_(
        identifier, content, trigger
    )
    
    center = UNUserNotificationCenter.currentNotificationCenter()
    center.addNotificationRequest_withCompletionHandler_(request, None)
