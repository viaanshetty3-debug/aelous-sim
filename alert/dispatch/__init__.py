"""Dispatch layer: convert a WarningPolygon + ThreatAssessment into Alerts
on every available channel, in parallel.

Three dispatcher classes:

- `WEADispatcher`           — carrier cell broadcast (CBC/SMPP direct injection)
- `IndoorPushDispatcher`    — APNs/FCM + smart-home / smart-speaker / smart-TV
- `SystemIntegrationDispatcher`
                            — EAS, highway signs, siren mesh, news-wire,
                              Apple/Google Weather feed injection, ISP banners
"""

from .wea import WEADispatcher
from .indoor_push import IndoorPushDispatcher
from .system_integration import SystemIntegrationDispatcher

__all__ = ["WEADispatcher", "IndoorPushDispatcher", "SystemIntegrationDispatcher"]
