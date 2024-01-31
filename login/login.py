from passlib.hash import bcrypt
from mapper import orm_mapper


def existing_user_check(login_name):
    results = orm_mapper.stmt_results()
    for row in results:
        if row.name == login_name:
            return row.id


def password_verification(input_p, user_id):
    hasher = bcrypt.using(rounds=13)
    results = orm_mapper.stmt_result_password(user_id)
    for row in results:
        if hasher.verify(input_p, row.hashed_password):
            return True
