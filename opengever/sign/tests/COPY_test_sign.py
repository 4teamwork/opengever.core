    def test_signed_version_created_as_user_who_started_sign_process(self, mocker):
        self.login(self.dossier_responsible)

        # prepare signing
        mocker.post(environ.get('SIGN_SERVICE_URL'), json=[])
        token = Signer(self.document).start_signing()

        Signer(self.document).add_signed_version(token, u'SIGNED_FILE_DATA')

        self.assertEqual(
            self.dossier_responsible.id,
            Versioner(self.document).get_version_metadata(1)['sys_metadata']['userid'])
