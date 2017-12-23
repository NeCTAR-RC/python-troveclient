#   Licensed under the Apache License, Version 2.0 (the "License"); you may
#   not use this file except in compliance with the License. You may obtain
#   a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#   WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#   License for the specific language governing permissions and limitations
#   under the License.

import mock

from osc_lib import exceptions
from osc_lib import utils

from troveclient import common
from troveclient.osc.v1 import database_clusters
from troveclient.tests.osc.v1 import fakes


class TestClusters(fakes.TestDatabasev1):
    fake_clusters = fakes.FakeClusters()

    def setUp(self):
        super(TestClusters, self).setUp()
        self.mock_client = self.app.client_manager.database
        self.cluster_client = self.app.client_manager.database.clusters


class TestClusterList(TestClusters):

    defaults = {
        'limit': None,
        'marker': None
    }

    columns = database_clusters.ListDatabaseClusters.columns
    values = ('cls-1234', 'test-clstr', 'vertica', '7.1', 'NONE')

    def setUp(self):
        super(TestClusterList, self).setUp()
        self.cmd = database_clusters.ListDatabaseClusters(self.app, None)
        data = [self.fake_clusters.get_clusters_cls_1234()]
        self.cluster_client.list.return_value = common.Paginated(data)

    def test_cluster_list_defaults(self):
        parsed_args = self.check_parser(self.cmd, [], [])
        columns, data = self.cmd.take_action(parsed_args)
        self.cluster_client.list.assert_called_once_with(**self.defaults)
        self.assertEqual(self.columns, columns)
        self.assertEqual([self.values], data)


class TestClusterShow(TestClusters):

    values = ('2015-05-02T10:37:04', 'vertica', '7.1', 'cls-1234', 2,
              'test-clstr', 'No tasks for the cluster.', 'NONE',
              '2015-05-02T11:06:19')

    def setUp(self):
        super(TestClusterShow, self).setUp()
        self.cmd = database_clusters.ShowDatabaseCluster(self.app, None)
        self.data = self.fake_clusters.get_clusters_cls_1234()
        self.cluster_client.get.return_value = self.data
        self.columns = (
            'created',
            'datastore',
            'datastore_version',
            'id',
            'instance_count',
            'name',
            'task_description',
            'task_name',
            'updated',
        )

    def test_show(self):
        args = ['cls-1234']
        parsed_args = self.check_parser(self.cmd, args, [])
        columns, data = self.cmd.take_action(parsed_args)
        self.assertEqual(self.columns, columns)
        self.assertEqual(self.values, data)


class TestDatabaseClusterDelete(TestClusters):

    def setUp(self):
        super(TestDatabaseClusterDelete, self).setUp()
        self.cmd = database_clusters.DeleteDatabaseCluster(self.app, None)

    @mock.patch.object(utils, 'find_resource')
    def test_cluster_delete(self, mock_find):
        args = ['cluster1']
        mock_find.return_value = args[0]
        parsed_args = self.check_parser(self.cmd, args, [])
        result = self.cmd.take_action(parsed_args)
        self.cluster_client.delete.assert_called_with('cluster1')
        self.assertIsNone(result)

    @mock.patch.object(utils, 'find_resource')
    def test_cluster_delete_with_exception(self, mock_find):
        args = ['fakecluster']
        parsed_args = self.check_parser(self.cmd, args, [])

        mock_find.side_effect = exceptions.CommandError
        self.assertRaises(exceptions.CommandError,
                          self.cmd.take_action,
                          parsed_args)