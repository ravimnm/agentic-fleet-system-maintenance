from database.mongo_client import MongoConnection


def seed():
    db = MongoConnection()

    # ---- Seed users ----
    users_coll = db.get_collection("users")
    if users_coll.estimated_document_count() == 0:
        users = [
            {"userId": "admin_1", "role": "admin"},
            {"userId": "user_12", "role": "user", "vehicleId": 12},
            {"userId": "user_5", "role": "user", "vehicleId": 5},
        ]
        users_coll.insert_many(users)
        print(f"Inserted {len(users)} sample users")
    else:
        print("Users collection already contains documents, skipping users seed")

    # ---- Seed service_centers ----
    centers_coll = db.get_collection("service_centers")
    if centers_coll.estimated_document_count() == 0:
        centers = [
            {"name": "Sai Motors", "latitude": 17.385, "longitude": 78.486, "rating": 4.6, "open_now": True},
            {"name": "Rapid Repair", "latitude": 17.400, "longitude": 78.480, "rating": 4.2, "open_now": True},
            {"name": "24/7 Auto Care", "latitude": 17.370, "longitude": 78.490, "rating": 4.8, "open_now": False},
        ]
        centers_coll.insert_many(centers)
        print(f"Inserted {len(centers)} sample service centers")
    else:
        print("Service_centers collection already contains documents, skipping centers seed")

    # ---- Seed risk_logs ----
    risk_coll = db.get_collection("risk_logs")
    if risk_coll.estimated_document_count() == 0:
        risks = [
            {
                "vehicleId": 12,
                "timestamp": "2025-12-16T00:00:00Z",
                "risk_score": 0.92,
                "category": "high",
                "reasons": ["engine_temp", "low_oil_pressure"],
            },
            {
                "vehicleId": 5,
                "timestamp": "2025-12-15T12:00:00Z",
                "risk_score": 0.45,
                "category": "medium",
                "reasons": ["brake_wear"],
            },
        ]
        risk_coll.insert_many(risks)
        print(f"Inserted {len(risks)} sample risk logs")
    else:
        print("risk_logs collection already contains documents, skipping risk seed")


if __name__ == "__main__":
    seed()

