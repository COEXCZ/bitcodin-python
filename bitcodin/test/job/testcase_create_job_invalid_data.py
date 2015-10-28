__author__ = 'Dominic Miglar <dominic.miglar@bitmovin.net>'

import unittest
from bitcodin import create_job
from bitcodin import create_input
from bitcodin import create_encoding_profile
from bitcodin import Job
from bitcodin import Input
from bitcodin import AudioStreamConfig
from bitcodin import VideoStreamConfig
from bitcodin import EncodingProfile
from bitcodin.exceptions import BitcodinBadRequestError
from bitcodin.test.config import test_video_url
from bitcodin.test.bitcodin_test_case import BitcodinTestCase


class CreateJobInvalidDataTestCase(BitcodinTestCase):
    def setUp(self):
        super(CreateJobInvalidDataTestCase, self).setUp()
        input_url = test_video_url
        input = Input(input_url)
        self.input = create_input(input)
        audio_stream_config = AudioStreamConfig(default_stream_id=0, bitrate=192000)
        video_stream_config = VideoStreamConfig(default_stream_id=0, bitrate=512000,
                                                profile='Main', preset='standard', height=480, width=640)
        encoding_profile = EncodingProfile('API Test Profile', [video_stream_config], [audio_stream_config])
        self.encoding_profile = create_encoding_profile(encoding_profile)

    def runTest(self):
        job = Job(
            input_id=self.input.input_id,
            encoding_profile_id=self.encoding_profile.encoding_profile_id,
            manifest_types=['m3u8', 'invalid']
        )
        with self.assertRaises(BitcodinBadRequestError):
            result = create_job(job)

    def tearDown(self):
        super(CreateJobInvalidDataTestCase, self).tearDown()


if __name__ == '__main__':
    unittest.main()
