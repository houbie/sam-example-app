import os

from botocore.session import Session
from pynamodb.attributes import UnicodeAttribute, UTCDateTimeAttribute
from pynamodb.models import Model


class S3Request(Model):
    """
    Lifecycle data for incoming S3 events
    """

    class Meta:
        table_name = os.environ.get("S3_REQUESTS_TABLE", "s3-requests")
        region = Session().get_config_variable("region")

    id = UnicodeAttribute(hash_key=True)
    process_name = UnicodeAttribute(attr_name="proc")
    functional_key = UnicodeAttribute(null=True, attr_name="funcKey")
    bucket = UnicodeAttribute(attr_name="bucket")
    s3_key = UnicodeAttribute(attr_name="s3_key")
    source_ip_address = UnicodeAttribute(null=True, attr_name="sourceIp")
    trace_id = UnicodeAttribute(null=True, attr_name="trace")
    received_time = UTCDateTimeAttribute(attr_name="received")
    processed_time = UTCDateTimeAttribute(null=True, attr_name="processed")
    error = UnicodeAttribute(null=True)
