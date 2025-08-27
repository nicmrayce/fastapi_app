from typing import Optional
try:
    import boto3  # optional
except Exception:
    boto3 = None

class S3Client:
    def __init__(self, *, access_key: Optional[str], secret_key: Optional[str], region: Optional[str]):
        self.enabled = bool(access_key and secret_key and region and boto3)
        if self.enabled:
            self._s3 = boto3.client(
                "s3",
                aws_access_key_id=access_key,
                aws_secret_access_key=secret_key,
                region_name=region,
            )
        else:
            self._s3 = None

    def upload_text(self, bucket: str, key: str, text: str) -> str:
        if not self.enabled or not self._s3:
            return f"s3://{bucket}/{key} (DRY-RUN)"
        self._s3.put_object(Bucket=bucket, Key=key, Body=text.encode("utf-8"))
        return f"s3://{bucket}/{key}"
