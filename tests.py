import requests
import unittest
import json
from random import choice

DEFAULT_HEADER = {'Content-Type': 'application/json'}

SUCCESS = 200
ABORTED = 400
CREATED = 201

TITLES = ('Sedoc', 'Medoc', 'Ass list', 'Bit data', 'Other')
TEXTS = ('do action', 'eat pie', 'make this test', 'capture world')
DUE_DATES = (1550046581, 1550046681, 1550047581)
STATUSES = ('true', 'false')

class TestTodoAPI(unittest.TestCase):

    def setUp(self):
        self.url = 'http://localhost:5000'
        self.lists = '/lists/'
        self.items = '/items/'
        self.list_ids = []
        self.item_ids = []
        self.test_post_list()
        self.test_post_item()

    def tearDown(self):
        for i in self.list_ids:
            requests.delete(
                self.url + self.lists + i,
            )

    def test_get_lists_list(self):
        response = requests.get(self.url + self.lists)
        self.assertEqual(response.status_code, SUCCESS)

    def test_post_list(self):
        title = choice(TITLES)
        payload = {
            'title': title
        }
        response = requests.post(
            self.url + self.lists,
            json=payload,
            headers=DEFAULT_HEADER
        )
        self.assertEqual(response.status_code, CREATED)
        self.assertEqual(response.json().get('title'), title)
        self.list_ids.append(response.json().get('_id')['$oid'])

    def test_get_list_by_id(self):
        list_id = choice(self.list_ids)
        response = requests.get(
            self.url + self.lists + list_id,
        )
        self.assertEqual(response.status_code, SUCCESS)
        self.assertIn(response.json()['title'], TITLES)

    def test_put_list_by_id(self):
        title = choice(TITLES)
        payload = {
            'title': title
        }
        list_id = choice(self.list_ids)
        response = requests.put(
            self.url + self.lists + list_id,
            json=payload,
            headers=DEFAULT_HEADER
        )
        self.assertEqual(response.status_code, SUCCESS)
        self.assertIn(response.json()['title'], TITLES)

    def test_delete_list_by_id(self):
        list_id = choice(self.list_ids)
        response = requests.delete(
            self.url + self.lists + list_id,
        )
        self.assertEqual(response.status_code, SUCCESS)
        self.assertEqual(response.json()['message'], "record deleted")

    def test_post_item(self):
        parent_id = choice(self.list_ids)
        text = choice(TEXTS)
        due_date = choice(DUE_DATES)
        finished_status = choice(STATUSES)
        payload = {
            'parent_id': parent_id,
            'text': text,
            'due_date': due_date,
            'finished_status': finished_status
        }
        response = requests.post(
            self.url + self.items,
            json=payload,
            headers=DEFAULT_HEADER
        )
        self.assertEqual(response.status_code, CREATED)
        self.assertEqual(response.json().get('_id')['$oid'], parent_id)

        items = response.json().get('items')
        for i in items:
            if i.get('_id')['$oid'] not in self.item_ids:
                self.item_ids.append(i.get('_id')['$oid'])
                self.assertEqual(i['text'], text)
                self.assertEqual(i['due_date']['$date'], due_date*1000)
                self.assertEqual(i['finished_status'], finished_status)

    def test_put_item(self):
        item_id = choice(self.item_ids)
        text = choice(TEXTS)
        due_date = choice(DUE_DATES)
        finished_status = choice(STATUSES)
        payload = {
            'text': text,
            'due_date': due_date,
            'finished_status': finished_status
        }
        response = requests.put(
            self.url + self.items + item_id,
            json=payload,
            headers=DEFAULT_HEADER
        )
        self.assertEqual(response.status_code, SUCCESS)
        items = response.json().get('items')
        for i in items:
            if i.get('_id')['$oid'] == item_id:
                self.assertEqual(i.get('text'), text)
                self.assertEqual(i.get('due_date')['$date'], due_date*1000)
                self.assertEqual(i.get('finished_status'), finished_status)

    def test_delete_item_by_id(self):
        item_id = choice(self.item_ids)
        response = requests.delete(
            self.url + self.items + item_id,
        )
        self.assertEqual(response.status_code, SUCCESS)
        self.assertEqual(response.json()['message'], "record deleted")


if __name__ == "__main__":
    unittest.main()