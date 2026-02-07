"""
Seed script to populate database with sample patients and visit logs
"""

import random
import datetime
from database import ClinicDatabase

# Filipino names for realistic data
FIRST_NAMES_MALE = [
    "Juan", "Pedro", "Jose", "Antonio", "Manuel", "Ricardo", "Roberto", "Carlos",
    "Miguel", "Fernando", "Eduardo", "Rafael", "Francisco", "Ramon", "Alejandro",
    "Gabriel", "Daniel", "Marco", "Paolo", "Jerico", "Bryan", "Mark", "John",
    "Michael", "Christopher", "Angelo", "Justin", "Kevin", "Ryan", "Jason"
]

FIRST_NAMES_FEMALE = [
    "Maria", "Ana", "Rosa", "Carmen", "Elena", "Teresa", "Patricia", "Gloria",
    "Luz", "Cristina", "Angela", "Rosario", "Esperanza", "Dolores", "Remedios",
    "Jennifer", "Michelle", "Nicole", "Jessica", "Ashley", "Samantha", "Grace",
    "Faith", "Joy", "Angel", "Princess", "Jasmine", "Ella", "Sofia", "Isabella"
]

MIDDLE_NAMES = [
    "Santos", "Cruz", "Reyes", "Garcia", "Ramos", "Mendoza", "Torres", "Flores",
    "Gonzales", "Bautista", "Villanueva", "Fernandez", "Dela Cruz", "Del Rosario",
    "Aquino", "Castro", "Rivera", "Diaz", "Lopez", "Martinez"
]

LAST_NAMES = [
    "Santos", "Reyes", "Cruz", "Bautista", "Ocampo", "Garcia", "Mendoza", "Torres",
    "Tomas", "Andrade", "Castillo", "Ramos", "Aquino", "Dela Cruz", "Rivera",
    "Gonzales", "Hernandez", "Lopez", "Martinez", "Rodriguez", "Fernandez",
    "Villanueva", "Del Rosario", "Aguilar", "Navarro", "Pascual", "Salvador",
    "Mercado", "Soriano", "Francisco"
]

ADDRESSES = [
    "123 Rizal St., Brgy. San Jose",
    "456 Mabini Ave., Brgy. Poblacion",
    "789 Bonifacio Rd., Brgy. Santo Nino",
    "321 Aguinaldo St., Brgy. San Miguel",
    "654 Luna St., Brgy. San Antonio",
    "987 Del Pilar Ave., Brgy. Santa Cruz",
    "147 Quezon Blvd., Brgy. San Pedro",
    "258 Osmeña St., Brgy. San Juan",
    "369 Roxas Ave., Brgy. San Isidro",
    "741 Marcos Highway, Brgy. Concepcion",
    "852 EDSA, Brgy. Bagong Silang",
    "963 Commonwealth Ave., Brgy. Holy Spirit",
    "159 Katipunan Ave., Brgy. Loyola Heights",
    "357 Aurora Blvd., Brgy. Mariana",
    "486 Shaw Blvd., Brgy. Wack Wack"
]

MEDICAL_NOTES = [
    "Regular checkup. Patient in good health.",
    "Complained of headache and mild fever. Prescribed paracetamol.",
    "Follow-up for hypertension. BP slightly elevated.",
    "Routine physical examination. All vitals normal.",
    "Patient reports fatigue and loss of appetite. Advised rest and hydration.",
    "Cough and cold symptoms. Prescribed antihistamine and cough syrup.",
    "Blood sugar monitoring. Fasting glucose within normal range.",
    "Back pain consultation. Recommended physical therapy.",
    "Annual checkup. Cholesterol levels slightly high. Dietary advice given.",
    "Flu-like symptoms. Advised bed rest and fluids.",
    "Skin rash examination. Prescribed topical cream.",
    "Digestive issues. Recommended dietary changes.",
    "Joint pain in knees. Anti-inflammatory medication prescribed.",
    "Respiratory checkup. Lungs clear, no issues found.",
    "General wellness visit. Patient maintaining healthy lifestyle.",
    "Allergic reaction follow-up. Symptoms have subsided.",
    "Dizziness and nausea. Blood tests ordered.",
    "Wound care and dressing change.",
    "Prenatal checkup. Mother and baby doing well.",
    "Post-operative follow-up. Healing progressing normally."
]


def generate_phone():
    """Generate random PH mobile number"""
    prefixes = ["0917", "0918", "0919", "0920", "0921", "0927", "0928", "0929", "0930", "0939", "0949", "0951"]
    return f"{random.choice(prefixes)}{random.randint(1000000, 9999999)}"


def generate_dob(min_age=18, max_age=85):
    """Generate random date of birth"""
    today = datetime.date.today()
    age = random.randint(min_age, max_age)
    year = today.year - age
    month = random.randint(1, 12)
    day = random.randint(1, 28)  # Safe day range
    return f"{year}-{month:02d}-{day:02d}"


def generate_visit_date(days_ago_max=365):
    """Generate random visit date within the past year"""
    today = datetime.date.today()
    days_ago = random.randint(0, days_ago_max)
    visit_date = today - datetime.timedelta(days=days_ago)
    return visit_date.strftime("%Y-%m-%d")


def generate_visit_time():
    """Generate random visit time during clinic hours"""
    hour = random.randint(8, 17)  # 8 AM to 5 PM
    minute = random.choice([0, 15, 30, 45])
    return f"{hour:02d}:{minute:02d}:00"


def generate_vitals():
    """Generate random but realistic vital signs"""
    weight = round(random.uniform(45, 95), 1) if random.random() > 0.2 else None
    height = round(random.uniform(150, 180), 1) if random.random() > 0.3 else None

    # Blood pressure
    if random.random() > 0.2:
        systolic = random.randint(100, 150)
        diastolic = random.randint(60, 95)
        bp = f"{systolic}/{diastolic}"
    else:
        bp = None

    temp = round(random.uniform(36.2, 37.8), 1) if random.random() > 0.3 else None

    return weight, height, bp, temp


def seed_database():
    """Populate database with sample data"""
    db = ClinicDatabase()

    print("Seeding database with sample data...")

    # Generate 30 patients
    patient_ids = []

    for i in range(30):
        # Random gender
        is_female = random.random() > 0.5

        if is_female:
            first_name = random.choice(FIRST_NAMES_FEMALE)
        else:
            first_name = random.choice(FIRST_NAMES_MALE)

        middle_name = random.choice(MIDDLE_NAMES) if random.random() > 0.2 else None
        last_name = random.choice(LAST_NAMES)
        dob = generate_dob()
        contact = generate_phone() if random.random() > 0.1 else None
        address = random.choice(ADDRESSES) if random.random() > 0.15 else None

        # Some patients have notes
        notes = None
        if random.random() > 0.7:
            note_options = [
                "Regular patient",
                "Senior citizen discount",
                "PWD - hearing impaired",
                "Diabetic - monitor blood sugar",
                "Hypertensive - monitor BP",
                "Allergic to penicillin",
                "Pregnant - 2nd trimester",
                "Post-surgery recovery"
            ]
            notes = random.choice(note_options)

        patient_id = db.add_patient(
            first_name=first_name,
            middle_name=middle_name,
            last_name=last_name,
            dob=dob,
            contact=contact,
            address=address,
            notes=notes
        )

        if patient_id:
            patient_ids.append(patient_id)
            print(f"  Added patient: {last_name}, {first_name}")

    print(f"\nAdded {len(patient_ids)} patients.")

    # Generate visit logs (1-5 visits per patient)
    visit_count = 0
    reference_number = 1

    # Create visits sorted by date
    all_visits = []

    for patient_id in patient_ids:
        num_visits = random.randint(1, 5)

        for _ in range(num_visits):
            visit_date = generate_visit_date()
            visit_time = generate_visit_time()
            weight, height, bp, temp = generate_vitals()
            notes = random.choice(MEDICAL_NOTES) if random.random() > 0.1 else None

            all_visits.append({
                'patient_id': patient_id,
                'visit_date': visit_date,
                'visit_time': visit_time,
                'weight': weight,
                'height': height,
                'bp': bp,
                'temp': temp,
                'notes': notes
            })

    # Sort visits by date (oldest first) so reference numbers are chronological
    all_visits.sort(key=lambda x: x['visit_date'])

    # Insert visits with sequential reference numbers
    for visit in all_visits:
        visit_id = db.add_visit(
            patient_id=visit['patient_id'],
            visit_date=visit['visit_date'],
            visit_time=visit['visit_time'],
            weight=visit['weight'],
            height=visit['height'],
            bp=visit['bp'],
            temp=visit['temp'],
            notes=visit['notes'],
            reference_number=reference_number
        )

        if visit_id:
            visit_count += 1
            reference_number += 1

    print(f"Added {visit_count} visit records.")
    print("\nDatabase seeding complete!")
    print(f"Total patients: {len(patient_ids)}")
    print(f"Total visit logs: {visit_count}")


if __name__ == "__main__":
    seed_database()
