import getpass
from hashlib import sha256
from Backend.PlayerCashRecordDB import PyBlackJackSQLLite


class PasswordComplexityError(Exception):
    ...


class _PasswordSetter:
    PASSWORD_COMPLEXITY_ERROR_MSG = ("Password must be at least 8 characters long and contain at least one number and "
                                     "one letter.")
    def __init__(self, candidate_pass: str):
        self.__password = candidate_pass
    @property
    def __password(self):
        return self._password

    @__password.setter
    def __password(self, password: str):
        if len(password) >= 8 and (any([x.isdigit() for x in password]) and any([x.isalpha() for x in password])):
            self._password = password
        else:
            raise PasswordComplexityError(_PasswordSetter.PASSWORD_COMPLEXITY_ERROR_MSG)

    def encrypt(self):
        return sha256(self.__password.encode()).hexdigest()


class PasswordValidator:
    def __init__(self, player_id, sql: PyBlackJackSQLLite):
        self._player_id = player_id
        self.sql = sql
        self._player_hash = None
        self._is_validated = None
    # TODO: add in create hash on player create

    @property
    def player_id(self):
        # TODO: check if player_id has changed, if it has then recheck hash
        return self._player_id

    @property
    def player_hash(self):
        if not self._player_hash:
            self._player_hash = self.sql.GetPlayerPasswordHash(self.player_id)
        return self._player_hash

    @property
    def is_validated(self):
        if not self._is_validated:
            self._is_validated =  sha256(getpass.getpass().encode()).hexdigest() == self.player_hash
        return self._is_validated



if __name__ == '__main__':
    pw = _PasswordSetter('password')
    print(pw.encrypt())