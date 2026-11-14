from flask import Flask, render_template, request, redirect, url_for
import mysql.connector
from weasyprint import HTML
from flask import make_response

app = Flask(__name__)

# ডাটাবেসের ঠিকানা ও লগইন
DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "",
    "database": "diagnostic_db"
}


# প্রতিবার ডাটাবেসে কানেক্ট করার ছোট ফাংশন
def get_db():
    return mysql.connector.connect(**DB_CONFIG)

@app.route("/")
def home():
    return render_template("home.html")

@app.route("/patients")
def patients():
    # ১. কানেক্ট
    conn = get_db()

    # ২. cursor = MySQL-এর সাথে কথা বলার "হাত"
    cursor = conn.cursor(dictionary=True)

    # ৩. SQL চালাও
    cursor.execute("SELECT * FROM patients ORDER BY id DESC")

    # ৪. সব ফলাফল নিয়ে নাও
    all_patients = cursor.fetchall()

    # ৫. ভালো অভ্যাস — সংযোগ বন্ধ 
    cursor.close()
    conn.close()

    # ৬. HTML-এ পাঠাও
    return render_template("patients.html", patients=all_patients)


@app.route("/patients/new", methods=["GET", "POST"])
def add_patient():
    if request.method == "POST":
        # ফর্ম থেকে ডেটা নাও
        name    = request.form["name"]
        phone   = request.form["phone"]
        gender  = request.form["gender"]
        age     = request.form["age"]
        address = request.form["address"]

        # ডাটাবেসে ঢোকাও
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute(
            """INSERT INTO patients (name, phone, gender, age, address)
               VALUES (%s, %s, %s, %s, %s)""",
            (name, phone, gender, age, address)
        )
        conn.commit()          # ← এটা লাগবে!
        cursor.close()
        conn.close()

        # কাজ শেষে তালিকায় ফেরত
        return redirect("/patients")

    # GET হলে ফাঁকা ফর্ম দেখাও
    return render_template(
        "patient_form.html",
        patient=None,
        action="/patients/new",
        title="নতুন রোগী যোগ করুন"
    )


@app.route("/patients/<int:patient_id>/delete", methods=["DELETE"])
def delete_patient(patient_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM patients WHERE id = %s", (patient_id,))
    conn.commit()
    cursor.close()
    conn.close()
    return ""   # খালি response — HTMX row-টা মুছে দেবে



@app.route("/patients/<int:patient_id>/edit", methods=["GET", "POST"])
def edit_patient(patient_id):
    if request.method == "POST":
        # ফর্ম থেকে নতুন ডেটা নাও
        name    = request.form["name"]
        phone   = request.form["phone"]
        gender  = request.form["gender"]
        age     = request.form["age"]
        address = request.form["address"]

        # ডাটাবেসে আপডেট
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute(
            """UPDATE patients
               SET name=%s, phone=%s, gender=%s, age=%s, address=%s
               WHERE id=%s""",
            (name, phone, gender, age, address, patient_id)
        )
        conn.commit()
        cursor.close()
        conn.close()

        return redirect("/patients")

    # GET হলে পুরনো ডেটা নিয়ে ফর্ম দেখাও
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM patients WHERE id = %s", (patient_id,))
    patient = cursor.fetchone()
    cursor.close()
    conn.close()

    if not patient:
        return "রোগী পাওয়া যায়নি", 404

    return render_template(
        "patient_form.html",
        patient=patient,
        action=f"/patients/{patient_id}/edit",
        title="রোগী সম্পাদনা"
    )




@app.route("/patients/search")
def search_patients():
    q = request.args.get("q", "").strip()

    conn = get_db()
    cursor = conn.cursor(dictionary=True)

    if q:
        # LIKE দিয়ে নাম বা ফোনে খোঁজো
        cursor.execute(
            """SELECT * FROM patients
               WHERE name LIKE %s OR phone LIKE %s
               ORDER BY id DESC""",
            (f"%{q}%", f"%{q}%")
        )
    else:
        # খালি খোঁজা = সব দেখাও
        cursor.execute("SELECT * FROM patients ORDER BY id DESC")

    patients = cursor.fetchall()
    cursor.close()
    conn.close()

    # শুধু rows partial পাঠাও
    return render_template("_patient_rows.html", patients=patients)



# ---------- TESTS ----------

@app.route("/tests")
def tests():
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM tests ORDER BY id DESC")
    all_tests = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template("tests.html", tests=all_tests)


@app.route("/tests/new", methods=["GET", "POST"])
def add_test():
    if request.method == "POST":
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute(
            """INSERT INTO tests (test_name, category, price, normal_range)
               VALUES (%s, %s, %s, %s)""",
            (
                request.form["test_name"],
                request.form["category"],
                request.form["price"],
                request.form["normal_range"],
            )
        )
        conn.commit()
        cursor.close()
        conn.close()
        return redirect("/tests")

    return render_template(
        "test_form.html",
        test=None,
        action="/tests/new",
        title="নতুন টেস্ট"
    )


@app.route("/tests/<int:test_id>/edit", methods=["GET", "POST"])
def edit_test(test_id):
    if request.method == "POST":
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute(
            """UPDATE tests
               SET test_name=%s, category=%s, price=%s, normal_range=%s
               WHERE id=%s""",
            (
                request.form["test_name"],
                request.form["category"],
                request.form["price"],
                request.form["normal_range"],
                test_id,
            )
        )
        conn.commit()
        cursor.close()
        conn.close()
        return redirect("/tests")

    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM tests WHERE id=%s", (test_id,))
    test = cursor.fetchone()
    cursor.close()
    conn.close()

    if not test:
        return "টেস্ট পাওয়া যায়নি", 404

    return render_template(
        "test_form.html",
        test=test,
        action=f"/tests/{test_id}/edit",
        title="টেস্ট সম্পাদনা"
    )


@app.route("/tests/<int:test_id>/delete", methods=["DELETE"])
def delete_test(test_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM tests WHERE id=%s", (test_id,))
    conn.commit()
    cursor.close()
    conn.close()
    return ""




# ---------- REPORTS ----------

@app.route("/reports")
def reports():
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT r.*, p.name as patient_name, p.phone
        FROM reports r
        JOIN patients p ON r.patient_id = p.id
        ORDER BY r.id DESC
    """)
    all_reports = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template("reports.html", reports=all_reports)


@app.route("/reports/new", methods=["GET", "POST"])
def add_report():
    if request.method == "POST":
        patient_id = request.form["patient_id"]
        test_ids = request.form.getlist("test_ids")

        if not patient_id or not test_ids:
            return "রোগী এবং অন্তত একটা টেস্ট বেছে নিন", 400

        conn = get_db()
        cursor = conn.cursor()

        # রিপোর্ট তৈরি
        cursor.execute(
            "INSERT INTO reports (patient_id, report_date) VALUES (%s, CURDATE())",
            (patient_id,)
        )
        report_id = cursor.lastrowid

        # প্রতিটা টেস্টের item ঢোকাও + দাম snapshot
        total = 0
        for tid in test_ids:
            cursor.execute("SELECT price FROM tests WHERE id=%s", (tid,))
            row = cursor.fetchone()
            if row:
                price = row[0]
                total += float(price)
                cursor.execute(
                    "INSERT INTO report_items (report_id, test_id, price) VALUES (%s, %s, %s)",
                    (report_id, tid, price)
                )

        cursor.execute("UPDATE reports SET total_amount=%s WHERE id=%s", (total, report_id))
        conn.commit()
        cursor.close()
        conn.close()

        return redirect(f"/reports/{report_id}")

    # GET — form
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM patients ORDER BY name")
    patients = cursor.fetchall()
    cursor.execute("SELECT * FROM tests ORDER BY category, test_name")
    tests = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template("report_form.html", patients=patients, tests=tests)


@app.route("/reports/<int:report_id>", methods=["GET", "POST"])
def view_report(report_id):
    conn = get_db()
    cursor = conn.cursor(dictionary=True)

    if request.method == "POST":
        # প্রতিটা রেজাল্ট সেভ করো
        for key, value in request.form.items():
            if key.startswith("result_"):
                item_id = key.replace("result_", "")
                cursor.execute(
                    "UPDATE report_items SET result_value=%s WHERE id=%s",
                    (value.strip(), item_id)
                )

        # সব রেজাল্ট হয়ে গেলে status = ready
        cursor.execute("""
            SELECT COUNT(*) as total,
                   SUM(CASE WHEN result_value IS NOT NULL AND result_value != '' THEN 1 ELSE 0 END) as filled
            FROM report_items WHERE report_id=%s
        """, (report_id,))
        stats = cursor.fetchone()
        if stats["total"] and stats["filled"] and stats["total"] == stats["filled"]:
            cursor.execute("UPDATE reports SET status='ready' WHERE id=%s", (report_id,))

        conn.commit()
        cursor.close()
        conn.close()
        return redirect(f"/reports/{report_id}")

    cursor.execute("""
        SELECT r.*, p.name as patient_name, p.phone, p.age, p.gender, p.address
        FROM reports r
        JOIN patients p ON r.patient_id = p.id
        WHERE r.id=%s
    """, (report_id,))
    report = cursor.fetchone()

    if not report:
        cursor.close()
        conn.close()
        return "রিপোর্ট পাওয়া যায়নি", 404

    cursor.execute("""
        SELECT ri.*, t.test_name, t.normal_range, t.category
        FROM report_items ri
        JOIN tests t ON ri.test_id = t.id
        WHERE ri.report_id=%s
    """, (report_id,))
    items = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template("report_view.html", report=report, items=items)


@app.route("/reports/<int:report_id>/pdf")
def report_pdf(report_id):
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT r.*, p.name as patient_name, p.phone, p.age, p.gender, p.address
        FROM reports r
        JOIN patients p ON r.patient_id = p.id
        WHERE r.id=%s
    """, (report_id,))
    report = cursor.fetchone()

    if not report:
        cursor.close()
        conn.close()
        return "রিপোর্ট পাওয়া যায়নি", 404

    cursor.execute("""
        SELECT ri.*, t.test_name, t.normal_range, t.category
        FROM report_items ri
        JOIN tests t ON ri.test_id = t.id
        WHERE ri.report_id=%s
    """, (report_id,))
    items = cursor.fetchall()
    cursor.close()
    conn.close()

    html = render_template("report_pdf.html", report=report, items=items)
    pdf = HTML(string=html).write_pdf()

    response = make_response(pdf)
    response.headers["Content-Type"] = "application/pdf"
    response.headers["Content-Disposition"] = f'inline; filename="report_{report_id}.pdf"'
    return response

if __name__ == "__main__":
    app.run(debug=True)