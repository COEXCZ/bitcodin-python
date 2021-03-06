__author__ = 'Dominic Miglar <dominic.miglar@bitmovin.net>'

import unittest
from time import sleep, time
from bitcodin import create_job, list_transfer_jobs
from bitcodin import create_input
from bitcodin import create_encoding_profile
from bitcodin import delete_input
from bitcodin import delete_encoding_profile
from bitcodin import transfer_job
from bitcodin import create_output
from bitcodin import delete_output
from bitcodin import get_job_status
from bitcodin import Job
from bitcodin import Input
from bitcodin import AudioStreamConfig
from bitcodin import VideoStreamConfig
from bitcodin import EncodingProfile
from bitcodin import S3Output
from bitcodin.exceptions import BitcodinError
from bitcodin.test.settings import s3_output_config
from bitcodin.test.config import test_video_url
from bitcodin.test.bitcodin_test_case import BitcodinTestCase


class TransferJobToS3TestCase(BitcodinTestCase):
    def setUp(self):
        super(TransferJobToS3TestCase, self).setUp()
        self.maxDiff = None

        input_url = test_video_url
        input = Input(input_url)
        self.input = create_input(input)
        audio_stream_config = AudioStreamConfig(default_stream_id=0, bitrate=192000)
        video_stream_config = VideoStreamConfig(default_stream_id=0, bitrate=512000,
                                                profile='Main', preset='premium', height=480, width=640)
        encoding_profile = EncodingProfile('API Test Profile', [video_stream_config], [audio_stream_config])
        self.encoding_profile = create_encoding_profile(encoding_profile)
        self.manifests = ['m3u8', 'mpd']
        job = Job(
            input_id=self.input.input_id,
            encoding_profile_id=self.encoding_profile.encoding_profile_id,
            manifest_types=self.manifests,
            speed='standard'
        )
        self.job = create_job(job)
        self.s3_configuration = {
            'name': 'Python API Test Output',
            'host': s3_output_config.get('host', None),
            'access_key': s3_output_config.get('access_key', None),
            'secret_key': s3_output_config.get('secret_key', None),
            'bucket': s3_output_config.get('bucket', None),
            'prefix': s3_output_config.get('prefix', None),
            'region': s3_output_config.get('region', None),
            'make_public': False
        }
        output = S3Output(
            name=self.s3_configuration.get('name'),
            host=self.s3_configuration.get('host'),
            access_key=self.s3_configuration.get('access_key'),
            secret_key=self.s3_configuration.get('secret_key'),
            bucket=self.s3_configuration.get('bucket'),
            prefix=self.s3_configuration.get('prefix'),
            region=self.s3_configuration.get('region'),
            make_public=self.s3_configuration.get('make_public')
        )
        self.output = create_output(output)

    def runTest(self):
        start_time = time()
        time_limit = 1200
        while True:
            job_status = get_job_status(self.job.job_id)
            if job_status.status.lower() == 'finished':
                break
            elif job_status.status.lower() == 'error':
                raise BitcodinError('An error occured while waiting for job to be FINISHED', 'Job status changed to ERROR!')
            elif time() - start_time > time_limit:
                raise BitcodinError('Timeout of job duration exceeded!', 'Job took too long!')
            sleep(2)
        transfer = transfer_job(self.job.job_id, self.output.output_id)
        self.assertEqual(transfer.job_id, self.job.job_id)
        transfer_jobs = list_transfer_jobs(self.job.job_id)
        self.assertEqual(len(transfer_jobs), 1)

    def tearDown(self):
        delete_input(self.input.input_id)
        delete_encoding_profile(self.encoding_profile.encoding_profile_id)
        delete_output(self.output.output_id)
        super(TransferJobToS3TestCase, self).tearDown()


if __name__ == '__main__':
    unittest.main()
