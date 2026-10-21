class ProviderTransientError(Exception):
    """The provider failed in a way that may succeed on a later request."""


class ProviderRateLimited(ProviderTransientError):
    """The provider exhausted its quota; do not retry within this operation."""


class ProviderPermanentError(Exception):
    """The provider rejected a request that should not be retried."""


class WeatherDataInvalid(Exception):
    """The provider response violates the weather data contract."""


class LocationNotFound(Exception):
    """The geocoding provider returned no usable location."""


class DependencyUnavailable(Exception):
    """An infrastructure dependency is unavailable."""


class WeatherProviderUnavailable(Exception):
    """The weather provider could not produce a forecast and no valid stale value exists."""


class LockOwnershipLost(WeatherProviderUnavailable):
    """The service lost the refresh lock while an upstream request was in progress."""
