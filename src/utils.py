from uuid import uuid4


# Combine database add & commit functions
def db_add_and_commit(db, model) -> None:
    db.session.add(model)
    db.session.commit()


# Get model as a list of dictionaries
def model_to_dict(model) -> list:
    return [row.to_dict() for row in model.query.all()]


# Generate a random hexadecimal value
def random_hex(max_length: int = 6) -> str:
    return uuid4().hex[:max_length]
