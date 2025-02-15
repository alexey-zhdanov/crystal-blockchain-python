from .base_module import Module
from ..utils import check_type


class Transfers(Module):
    _ADD_TX_TO_CUSTOMER = '/monitor/tx/add'
    _EDIT_TX = '/monitor/tx/{id}/edit'
    _UPDATE_TX = '/monitor/tx/{id}/update'
    _GET_CUSTOMER_TXS = '/monitor/one/{token}/txs'
    _GET_TX_BOUNDS = '/monitor/one/{token}/tx-bounds'
    _EDIT_CUSTOMER_TXS = '/monitor/one/{token}/txs/execute'

    _DIRECTIONS_1 = ('deposit', 'withdrawal')
    _FLAGS = ('flag', 'unflag')
    _WITH_TOTALS = (0, 1)
    _ORDERS = ('amount', 'fiat', 'time', 'created_at', 'updated_at', 'riskscore')
    _DIRECTIONS_2 = ('asc', 'desc')
    _ACTIONS = ('schedule', 'archive', 'unarchive', 'flag', 'unflag')

    def add_tx_to_customer(self, tx: str, direction: str, address: str, name: str) -> dict:
        """
        Adding transactions to the existing customer or creating a new customer

        :param tx: Transaction hash (ex. 'f00ddb52671bcdddfb1bb654c091320f624e443edba392ea27e178817048b776')
        :param direction: Type of the transaction ('deposit' or 'withdrawal')
        :param address: The received of the transfer (the address must be in the transaction outputs)
        (ex. '1AxCHtZA1mxNLg2o6KPRCyDRueifLPXED')
        :param name: Customer name (if there is no customer with this name, new customer will be created)
        :return:
        {
          "data": {
            "address": "1AxCHtZA1mxNLg2o6KPRCyDRueifLPXED",
            "amount": 420060000,
            "archived": true,
            "created_at": 1571653914,
            "customer": {
              "name": "C#1456",
              "token": "bn3KXb66HkncoJPv"
            },
            "direction": "deposit",
            "fiat_code_effective": "eur",
            "flagged": false,
            "flag_reason": [...],
            "reason": null,
            "id": 1010,
            "riskscore": 0,
            "riskscore_profile": {
              "id": 10,
              "name": "KYC profile",
              "history_id": 322
            },
            "risky_volume": 12345.667,
            "risky_volume_fiat": 112,
            "signals": {
            ...
            },
            "status": "ready",
            "time": 1571652931,
            "token_id": 0,
            "tx": "f00ddb52671bcdddfb1bb654c091320f624e443edba392ea27e178817048b776",
            "updated_at": 1571653914,
            "fiat": 3449426
          },
          "meta": {
            "calls_left": 0,
            "calls_used": 0,
            "error_code": 0,
            "error_message": "string",
            "fiat_code": "usd",
            "riskscore_profile": {
              "id": 150,
              "name": "default"
            },
            "server_time": 0,
            "validation_errors": {}
          }
        }
        """
        check_type(tx, str)
        if not (direction in self._DIRECTIONS_1):
            raise ValueError('Check "direction" value')
        check_type(address, str)
        check_type(name, str)

        # Token identifier. Enter 1 for USDT transfers, otherwise enter 0 or delete this field.
        token_id = self._crystal.TOKEN_ID

        params = {
            'token_id': token_id,
            'tx': tx,
            'direction': direction,
            'address': address,
            'name': name
        }
        response = self._crystal.session().post(
            url=self._to_endpoint(self._ADD_TX_TO_CUSTOMER),
            params=params
        )

        self._raise_for_error(response)

        return response.json()

    def edit_tx(self, transfer_id: str, archived=None, flagged=None) -> dict:
        """
        Moving transfers to archive or restoring from archive, flagging or unflaggind transfers

        :param transfer_id: Transfer id
        :param archived: Select True to archive transfer and False to unarchive
        :param flagged: 'flag' or 'unflag'
        :return:
        {
          "meta": {
            "calls_left": 0,
            "calls_used": 0,
            "error_code": 0,
            "error_message": "string",
            "fiat_code": "usd",
            "riskscore_profile": {
              "id": 150,
              "name": "default"
            },
            "server_time": 0,
            "validation_errors": {}
          }
        }
        """
        check_type(transfer_id, str)

        params = {}
        if archived:
            check_type(archived, bool)
            params['archived'] = archived
        if flagged:  # NOTE: кажется, параметр не воспринимается в API
            if not (flagged in self._FLAGS):
                raise ValueError('Check "flagged" value')
            params['flagged'] = flagged

        response = self._crystal.session().post(
            url=self._to_endpoint(self._EDIT_TX.format(id=transfer_id)),
            params=params
        )

        self._raise_for_error(response)

        return response.json()

    def update_tx(self, transfer_id: str) -> dict:
        """
        Moving transfers to archive or restoring from archive, flagging or unflaggind transfers

        :param transfer_id: Transfer id
        :return:
        {
          "data": {
            "address": "1AxCHtZA1mxNLg2o6KPRCyDRueifLPXED",
            "amount": 420060000,
            "archived": true,
            "created_at": 1571653914,
            "customer": {
              "name": "C#1456",
              "token": "bn3KXb66HkncoJPv"
            },
            "direction": "deposit",
            "fiat_code_effective": "eur",
            "flagged": false,
            "flag_reason": [
             ...
            ],
            "reason": null,
            "id": 1010,
            "riskscore": 0,
            "riskscore_profile": {
              "id": 10,
              "name": "KYC profile",
              "history_id": 322
            },
            "risky_volume": 12345.667,
            "risky_volume_fiat": 112,
            "signals": {
              ...
            },
            "status": "ready",
            "time": 1571652931,
            "token_id": 0,
            "tx": "f00ddb52671bcdddfb1bb654c091320f624e443edba392ea27e178817048b776",
            "updated_at": 1571653914,
            "fiat": 3449426
          },
          "meta": {
            ...
          }
        }
        """
        check_type(transfer_id, str)

        response = self._crystal.session().post(
            url=self._to_endpoint(self._UPDATE_TX.format(id=transfer_id)),
        )

        self._raise_for_error(response)

        return response.json()

    def get_customer_txs(
            self,
            token: str,
            with_total=None,
            offset=None,
            limit=None,
            order=None,
            direction=None,
            filter_dict=None

    ) -> dict:
        """
        Get list of transfers with applied filters

        :param token: Token corresponding to the customer
        :param with_total: number, default=0 (0 or 1)
        :param offset: number, default=0
        :param limit: The value ranges between 1 and 20000, number, example=10
        :param order: string, default='updated_at' ('amount', 'fiat', 'time', 'created_at', 'updated_at', 'riskscore')
        :param direction: direction, string ('asc', 'desc' )
        :param filter_dict: filter dictionary, see API
        :return:
        """
        check_type(token, str)

        params = {}

        if with_total:
            if with_total not in self._WITH_TOTALS:
                raise ValueError('Check "with_total" value')
            params['with_total'] = with_total
        if offset:
            params['offset'] = offset
        if limit:
            params['limit'] = limit
        if order:
            if order not in self._ORDERS:
                raise ValueError('Check "order" value')
            params['order'] = order
        if direction:
            if direction not in self._DIRECTIONS_2:
                raise ValueError('Check "direction" value')
            params['direction'] = direction
        if filter_dict:
            check_type(filter_dict, dict)
            params['filter'] = self._filter_to_str(filter_dict)
        response = self._crystal.session().post(
            url=self._to_endpoint(self._GET_CUSTOMER_TXS.format(token=token)),
            params=params
        )

        self._raise_for_error(response)

        return response.json()

    def get_tx_bounds(self, token: str) -> dict:
        """
        Get minimum and maximum filtering parameters

        :param token: Token corresponding to the customer
        :return:
        {
          "data": {
            "created_min": 1561107720,
            "created_max": 1561107720,
            "updated_min": 1561108012,
            "updated_max": 1561108012,
            "time_min": 1561107421,
            "time_max": 1561107421,
            "amount": 20790475596,
            "fiat": 202748821
          },
          "meta": {
            "calls_left": 0,
            "calls_used": 0,
            "error_code": 0,
            "error_message": "string",
            "fiat_code": "usd",
            "riskscore_profile": {
              "id": 150,
              "name": "default"
            },
            "server_time": 0,
            "validation_errors": {}
          }
        }
        """
        check_type(token, str)

        response = self._crystal.session().get(
            url=self._to_endpoint(self._GET_TX_BOUNDS.format(token=token)),
        )

        self._raise_for_error(response)

        return response.json()

    def edit_customer_txs(
            self,
            token: str,
            action=None,
            filter_dict=None
    ) -> dict:
        """
        Get minimum and maximum filtering parameters

        :param token: Token corresponding to the customer
        :param action: Here you can specify the action ('schedule', 'archive', 'unarchive', 'flag', 'unflag')
        :param filter_dict: filter dict (see API docs)
        :return:
        {
            "data": {
                "scheduled": 1,
                "archived": 1,
                "unarchived": 1
            },
            "meta": {
                "calls_left": 0,
                "calls_used": 0,
                "error_code": 0,
                "error_message": "string",
                "fiat_code": "usd",
                "riskscore_profile": {
                    "id": 150,
                    "name": "default"
                },
                "server_time": 0,
                "validation_errors": {}
            }
        }
        """
        params = {}

        if action:
            if not (action in self._ACTIONS):
                raise ValueError('Check "action" value')
            params['action'] = action
        if filter_dict:
            check_type(filter_dict, dict)
            params['filter'] = self._filter_to_str(filter_dict)

        response = self._crystal.session().post(
            url=self._to_endpoint(self._EDIT_CUSTOMER_TXS.format(token=token)),
            params=params
        )

        self._raise_for_error(response)

        return response.json()
