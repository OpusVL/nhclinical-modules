from openerp.tests.common import SingleTransactionCase
from openerp.osv.orm import except_orm
from datetime import datetime as dt, timedelta as td
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT as dtf


class TestCoreAPI(SingleTransactionCase):

    @classmethod
    def setUpClass(cls):
        super(TestCoreAPI, cls).setUpClass()
        cr, uid = cls.cr, cls.uid

        cls.users_pool = cls.registry('res.users')
        cls.groups_pool = cls.registry('res.groups')
        cls.partner_pool = cls.registry('res.partner')
        cls.activity_pool = cls.registry('nh.activity')
        cls.patient_pool = cls.registry('nh.clinical.patient')
        cls.location_pool = cls.registry('nh.clinical.location')
        cls.pos_pool = cls.registry('nh.clinical.pos')
        cls.api = cls.registry('nh.clinical.api')

        cls.wm_group_id = cls.groups_pool.search(cr, uid, [['name', '=', 'NH Clinical Ward Manager Group']])
        cls.nurse_group_id = cls.groups_pool.search(cr, uid, [['name', '=', 'NH Clinical Nurse Group']])
        cls.hca_group_id = cls.groups_pool.search(cr, uid, [['name', '=', 'NH Clinical HCA Group']])
        cls.doctor_group_id = cls.groups_pool.search(cr, uid, [['name', '=', 'NH Clinical Doctor Group']])
        cls.admin_group_id = cls.groups_pool.search(cr, uid, [['name', '=', 'NH Clinical Admin Group']])

        cls.hospital_id = cls.location_pool.create(cr, uid, {'name': 'Test Hospital', 'code': 'TESTHOSP',
                                                             'usage': 'hospital'})
        cls.pos_id = cls.pos_pool.create(cr, uid, {'name': 'Test POS', 'location_id': cls.hospital_id})

        cls.adt_uid = cls.users_pool.create(cr, uid, {'name': 'Admin 0', 'login': 'user_000',
                                                        'password': 'user_000',
                                                        'groups_id': [[4, cls.admin_group_id[0]]],
                                                        'pos_id': cls.pos_id})

        cls.locations = {}
        for i in range(3):
            wid = cls.location_pool.create(cr, uid, {'name': 'Ward'+str(i), 'code': 'WARD'+str(i), 'usage': 'ward',
                                                     'parent_id': cls.hospital_id, 'type': 'poc'})
            cls.locations[wid] = [cls.location_pool.create(cr, uid, {'name': 'Bed'+str(i)+str(j),
                                                                     'code': 'BED'+str(i)+str(j),
                                                                     'usage': 'bed', 'parent_id': wid,
                                                                     'type': 'poc'}) for j in range(3)]

    def test_01_register(self):
        cr, uid = self.cr, self.uid

        # Scenario 1: Register a patient with Hospital Number
        patient_data = {
            'family_name': "Fname",
            'given_name': 'Gname',
            'dob': '1988-08-14 18:00:00',
            'gender': 'M',
            'sex': 'M'
        }

        self.api.register(cr, self.adt_uid, 'TESTP0001', patient_data)

        patient_id = self.patient_pool.search(cr, uid, [('other_identifier', '=', 'TESTP0001')])
        self.assertTrue(patient_id, msg="Patient was not created")
        activity_id = self.activity_pool.search(cr, uid, [
            ['data_model', '=', 'nh.clinical.adt.patient.register'], ['patient_id', '=', patient_id[0]]])
        self.assertTrue(activity_id, msg="Register Activity not generated")
        activity = self.activity_pool.browse(cr, uid, activity_id[0])
        self.assertEqual(activity.state, 'completed')

        # Scenario 2: Register a patient with NHS Number
        patient_data = {
            'patient_identifier': 'TESTNHS001',
            'family_name': "Fname2",
            'given_name': 'Gname2',
            'gender': 'F',
            'sex': 'F'
        }

        self.api.register(cr, self.adt_uid, '', patient_data)

        patient_id = self.patient_pool.search(cr, uid, [('patient_identifier', '=', 'TESTNHS001')])
        self.assertTrue(patient_id, msg="Patient was not created")
        activity_id = self.activity_pool.search(cr, uid, [
            ['data_model', '=', 'nh.clinical.adt.patient.register'], ['patient_id', '=', patient_id[0]]])
        self.assertTrue(activity_id, msg="Register Activity not generated")
        activity = self.activity_pool.browse(cr, uid, activity_id[0])
        self.assertEqual(activity.state, 'completed')

    def test_02_update(self):
        cr, uid = self.cr, self.uid

        # Scenario 1: Update a patient using Hospital Number
        patient_data = {
            'family_name': "Fname0",
            'given_name': 'Gname0',
            'dob': '1988-08-14 18:00:00',
            'gender': 'M',
            'sex': 'M'
        }
        
        self.api.update(cr, self.adt_uid, 'TESTP0001', patient_data)
        
        patient_id = self.patient_pool.search(cr, uid, [('other_identifier', '=', 'TESTP0001')])[0]
        activity_id = self.activity_pool.search(cr, uid, [
            ['data_model', '=', 'nh.clinical.adt.patient.update'], ['patient_id', '=', patient_id]])
        self.assertTrue(activity_id, msg="Update Activity not generated")
        activity = self.activity_pool.browse(cr, uid, activity_id[0])
        self.assertEqual(activity.state, 'completed')

        # Scenario 2: Update a patient using NHS Number
        patient_data = {
            'patient_identifier': 'TESTNHS001',
            'family_name': "Fname20",
            'given_name': 'Gname20',
            'dob': '1988-08-14 18:00:00',
            'gender': 'F',
            'sex': 'F'
        }

        self.api.update(cr, self.adt_uid, '', patient_data)

        patient_id = self.patient_pool.search(cr, uid, [('patient_identifier', '=', 'TESTNHS001')])[0]
        activity_id = self.activity_pool.search(cr, uid, [
            ['data_model', '=', 'nh.clinical.adt.patient.update'], ['patient_id', '=', patient_id]])
        self.assertTrue(activity_id, msg="Update Activity not generated")
        activity = self.activity_pool.browse(cr, uid, activity_id[0])
        self.assertEqual(activity.state, 'completed')

        # Scenario 3: Update a patient that does not exist. Automatic register
        patient_data = {
            'patient_identifier': 'TESTNHS003',
            'family_name': "Fname30",
            'given_name': 'Gname30',
            'dob': '1988-08-14 18:00:00',
            'gender': 'M',
            'sex': 'M'
        }

        self.api.update(cr, self.adt_uid, 'TESTP0003', patient_data)

        patient_id = self.patient_pool.search(cr, uid, [('other_identifier', '=', 'TESTP0003')])
        self.assertTrue(patient_id, msg="Patient was not created")
        activity_id = self.activity_pool.search(cr, uid, [
            ['data_model', '=', 'nh.clinical.adt.patient.update'], ['patient_id', '=', patient_id[0]]])
        self.assertTrue(activity_id, msg="Update Activity not generated")
        activity = self.activity_pool.browse(cr, uid, activity_id[0])
        self.assertEqual(activity.state, 'completed')

    def test_03_admit(self):
        cr, uid = self.cr, self.uid

        # Scenario 1: Admit a patient using Hospital Number
        admit_data = {'location': "WARD0"}

        self.api.admit(cr, self.adt_uid, 'TESTP0001', admit_data)

        patient_id = self.patient_pool.search(cr, uid, [('other_identifier', '=', 'TESTP0001')])[0]
        activity_id = self.activity_pool.search(cr, uid, [
            ['data_model', '=', 'nh.clinical.adt.patient.admit'], ['patient_id', '=', patient_id]])
        self.assertTrue(activity_id, msg="Admit Activity not generated")
        activity = self.activity_pool.browse(cr, uid, activity_id[0])
        self.assertEqual(activity.state, 'completed')

        # Scenario 2: Admit a patient using NHS Number
        admit_data = {'location': "WARD1", 'patient_identifier': 'TESTNHS001'}

        self.api.admit(cr, self.adt_uid, '', admit_data)

        patient_id = self.patient_pool.search(cr, uid, [('patient_identifier', '=', 'TESTNHS001')])[0]
        activity_id = self.activity_pool.search(cr, uid, [
            ['data_model', '=', 'nh.clinical.adt.patient.admit'], ['patient_id', '=', patient_id]])
        self.assertTrue(activity_id, msg="Admit Activity not generated")
        activity = self.activity_pool.browse(cr, uid, activity_id[0])
        self.assertEqual(activity.state, 'completed')

        # Scenario 3: Admit a patient that does not exist. Automatic register
        admit_data = {
            'location': "WARD2",
            'patient_identifier': 'TESTNHS004',
            'family_name': "Fname400",
            'given_name': 'Gname400',
            'dob': '1988-08-14 18:00:00',
            'gender': 'M',
            'sex': 'M'
            }

        self.api.admit(cr, self.adt_uid, 'TESTP0004', admit_data)

        patient_id = self.patient_pool.search(cr, uid, [('other_identifier', '=', 'TESTP0004')])
        self.assertTrue(patient_id, msg="Patient was not created")
        activity_id = self.activity_pool.search(cr, uid, [
            ['data_model', '=', 'nh.clinical.adt.patient.admit'], ['patient_id', '=', patient_id[0]]])
        self.assertTrue(activity_id, msg="Admit Activity not generated")
        activity = self.activity_pool.browse(cr, uid, activity_id[0])
        self.assertEqual(activity.state, 'completed')

    def test_04_admit_update(self):
        cr, uid = self.cr, self.uid

        # Scenario 1: Update admission using Hospital Number
        update_data = {'location': "WARD1"}

        self.api.admit_update(cr, self.adt_uid, 'TESTP0001', update_data)

        patient_id = self.patient_pool.search(cr, uid, [('other_identifier', '=', 'TESTP0001')])[0]
        activity_id = self.activity_pool.search(cr, uid, [
            ['data_model', '=', 'nh.clinical.adt.spell.update'], ['patient_id', '=', patient_id]])
        self.assertTrue(activity_id, msg="Spell Update Activity not generated")
        activity = self.activity_pool.browse(cr, uid, activity_id[0])
        self.assertEqual(activity.state, 'completed')

        # Scenario 2: Update admission using NHS Number
        update_data = {'location': "WARD2", 'patient_identifier': 'TESTNHS001'}

        self.api.admit_update(cr, self.adt_uid, '', update_data)

        patient_id = self.patient_pool.search(cr, uid, [('patient_identifier', '=', 'TESTNHS001')])[0]
        activity_id = self.activity_pool.search(cr, uid, [
            ['data_model', '=', 'nh.clinical.adt.spell.update'], ['patient_id', '=', patient_id]])
        self.assertTrue(activity_id, msg="Spell Update Activity not generated")
        activity = self.activity_pool.browse(cr, uid, activity_id[0])
        self.assertEqual(activity.state, 'completed')

        # Scenario 3: Update admission of a patient that does not exist. Automatic register and admission
        update_data = {
            'location': "WARD0",
            'patient_identifier': 'TESTNHS005',
            'family_name': "Fname5000",
            'given_name': 'Gname5000',
            'dob': '1988-08-14 18:00:00',
            'gender': 'F',
            'sex': 'F'
            }

        self.api.admit_update(cr, self.adt_uid, 'TESTP0005', update_data)

        patient_id = self.patient_pool.search(cr, uid, [('other_identifier', '=', 'TESTP0005')])
        self.assertTrue(patient_id, msg="Patient was not created")
        activity_id = self.activity_pool.search(cr, uid, [
            ['data_model', '=', 'nh.clinical.adt.spell.update'], ['patient_id', '=', patient_id[0]]])
        self.assertTrue(activity_id, msg="Admit Activity not generated")
        activity = self.activity_pool.browse(cr, uid, activity_id[0])
        self.assertEqual(activity.state, 'completed')

    def test_05_cancel_admit(self):
        cr, uid = self.cr, self.uid

        # Scenario 1: Cancel an admission
        self.api.cancel_admit(cr, self.adt_uid, 'TESTP0004')
        patient_id = self.patient_pool.search(cr, uid, [('other_identifier', '=', 'TESTP0004')])[0]
        activity_id = self.activity_pool.search(cr, uid, [
            ['data_model', '=', 'nh.clinical.adt.patient.cancel_admit'], ['patient_id', '=', patient_id]])
        self.assertTrue(activity_id, msg="Cancel Admission Activity not generated")
        activity = self.activity_pool.browse(cr, uid, activity_id[0])
        self.assertEqual(activity.state, 'completed')

        # Scenario 2: Cancel an admission of patient that does not exist
        with self.assertRaises(except_orm):
            self.api.cancel_admit(cr, self.adt_uid, 'TESTP0006')