from __future__ import annotations

import csv
from pathlib import Path


FIELDNAMES = [
    "age",
    "prior_admissions_180d",
    "emergency_visits_180d",
    "comorbidity_count",
    "medication_count",
    "abnormal_lab_count",
    "label_readmitted_30d",
]


def main() -> None:
    output_path = Path("data/synthetic_training_rows.csv")
    output_path.parent.mkdir(exist_ok=True)
    rows = []
    for idx in range(120):
        age = 35 + (idx * 7) % 55
        prior = idx % 4
        ed = (idx // 3) % 3
        comorbidity = (idx // 5) % 7
        medications = 1 + (idx // 2) % 9
        abnormal_labs = (idx // 7) % 4
        risk_points = prior * 2 + ed + comorbidity + abnormal_labs + int(age >= 75)
        rows.append(
            {
                "age": age,
                "prior_admissions_180d": prior,
                "emergency_visits_180d": ed,
                "comorbidity_count": comorbidity,
                "medication_count": medications,
                "abnormal_lab_count": abnormal_labs,
                "label_readmitted_30d": int(risk_points >= 6),
            }
        )

    with output_path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=FIELDNAMES)
        writer.writeheader()
        writer.writerows(rows)
    print(f"Wrote {len(rows)} synthetic rows to {output_path}")


if __name__ == "__main__":
    main()

