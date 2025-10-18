class Owner:
    def __init__(
        self,
        _id: int,
        name: str,
        contact_info: str,
        rating: float,
        is_real_estate_agent: bool = False,
    ):
        self.id = _id
        self.name = name
        self.contact_info = contact_info
        self.rating = rating
        self.is_real_estate_agent = is_real_estate_agent

    def __repr__(self):
        return (
            f"Owner(id={self.id}, name='{self.name}', contact_info={self.contact_info})"
        )
