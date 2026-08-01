import os
import sqlite3
import json
import re
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS

app = Flask(__name__, static_folder='.', static_url_path='')
CORS(app)

DB_FILE = 'vidyaquest.db'

def get_db():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    cursor = conn.cursor()

    # Students table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            xp INTEGER DEFAULT 0,
            streak INTEGER DEFAULT 0,
            level INTEGER DEFAULT 1,
            class_name TEXT DEFAULT 'Class 8',
            state TEXT DEFAULT 'Maharashtra',
            math_score INTEGER DEFAULT 0,
            science_score INTEGER DEFAULT 0,
            tech_score INTEGER DEFAULT 0,
            eng_score INTEGER DEFAULT 0,
            env_score INTEGER DEFAULT 0
        )
    ''')

    # Teachers table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS teachers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            school TEXT DEFAULT ''
        )
    ''')

    # Parents table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS parents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            child_username TEXT NOT NULL,
            relation TEXT DEFAULT 'Parent'
        )
    ''')

    # Questions table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS questions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            subject TEXT NOT NULL,
            question TEXT NOT NULL,
            opt_a TEXT NOT NULL,
            opt_b TEXT NOT NULL,
            opt_c TEXT NOT NULL,
            opt_d TEXT NOT NULL,
            answer_idx INTEGER NOT NULL,
            explanation TEXT DEFAULT '',
            class_name TEXT DEFAULT 'All'
        )
    ''')

    # Rooms table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS rooms (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            code TEXT UNIQUE NOT NULL,
            subject TEXT NOT NULL
        )
    ''')

    # Room Students table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS room_students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            room_code TEXT NOT NULL,
            student_username TEXT NOT NULL,
            score INTEGER DEFAULT 0
        )
    ''')

    # Seed initial STEM questions if empty
    cursor.execute('SELECT COUNT(*) FROM questions')
    if cursor.fetchone()[0] == 0:
        default_questions = [
            # Mathematics
            ('math', 'If 3x + 7 = 22, what is x?', 'x=3', 'x=4', 'x=5', 'x=6', 2, '3×5+7=22 ✓', 'All'),
            ('math', 'Area of circle with radius 7cm? (π≈22/7)', '154 cm²', '44 cm²', '49 cm²', '308 cm²', 0, 'π×r²=22/7×49=154', 'All'),
            ('math', 'What is 15% of 240?', '36', '24', '48', '30', 0, '15/100×240=36', 'All'),
            ('math', 'Solve for y: 2y - 10 = 4y + 2', 'y=-6', 'y=6', 'y=-4', 'y=4', 0, '-12=2y → y=-6', 'All'),
            ('math', 'What is the square root of 225?', '13', '15', '25', '17', 1, '15×15=225', 'All'),
            ('math', 'Sum of angles in a pentagon?', '360°', '540°', '720°', '180°', 1, '(n-2)×180 = 3×180 = 540°', 'All'),
            ('math', 'A car travels 150km in 3 hours. Speed?', '45 km/h', '50 km/h', '60 km/h', '30 km/h', 1, '150/3 = 50', 'All'),
            ('math', 'Probability of rolling a 4 on a 6-sided die?', '1/6', '1/2', '1/4', '1/3', 0, 'One 4 out of 6 faces', 'All'),
            
            # Science
            ('science', "Newton's 2nd Law: Force equals?", 'Mass×Velocity', 'Mass×Acceleration', 'Weight×Distance', 'Speed×Time', 1, 'F=ma', 'All'),
            ('science', 'Gas plants absorb in photosynthesis?', 'Oxygen', 'Nitrogen', 'Carbon Dioxide', 'Hydrogen', 2, 'CO₂+water+sunlight→glucose+oxygen', 'All'),
            ('science', 'What is the PH of pure water?', '0', '7', '14', '5', 1, 'Pure water is neutral (PH 7)', 'All'),
            ('science', 'Smallest bone in the human body?', 'Femur', 'Stapes', 'Humerus', 'Tibia', 1, 'The stapes is in the ear', 'All'),
            ('science', 'Planet known as the Red Planet?', 'Venus', 'Jupiter', 'Mars', 'Saturn', 2, 'Iron oxide makes Mars look red', 'All'),
            ('science', 'Speed of light approximately?', '300,000 km/s', '150,000 km/s', '1,000,000 km/s', '50,000 km/s', 0, '3×10⁸ m/s = 300,000 km/s', 'All'),
            ('science', 'Hardest natural substance on Earth?', 'Gold', 'Iron', 'Diamond', 'Graphite', 2, 'Diamond is pure carbon in crystal form', 'All'),

            # Technology
            ('tech', 'CPU stands for?', 'Central Processing Unit', 'Computer Power Unit', 'Central Program Utility', 'Core Processing Unit', 0, 'CPU = Central Processing Unit', 'All'),
            ('tech', 'Language for web pages?', 'Python', 'Java', 'HTML', 'C++', 2, 'HTML structures web pages', 'All'),
            ('tech', 'Who co-founded Microsoft?', 'Steve Jobs', 'Bill Gates', 'Mark Zuckerberg', 'Jeff Bezos', 1, 'Bill Gates and Paul Allen', 'All'),
            ('tech', 'Binary system uses which digits?', '1 and 2', '0 and 1', '0-9', 'A-F', 1, '0 and 1 (Base-2)', 'All'),
            ('tech', 'What does RAM stand for?', 'Read Access Memory', 'Random Access Memory', 'Rapid Action Memory', 'Real Access Module', 1, 'RAM = Random Access Memory', 'All'),
            ('tech', 'A byte consists of how many bits?', '4', '8', '16', '32', 1, '8 bits = 1 byte', 'All'),
            ('tech', 'Which protocol is for secure web browsing?', 'HTTP', 'HTTPS', 'FTP', 'SMTP', 1, 'HTTPS uses SSL/TLS', 'All'),

            # Engineering
            ('eng', 'Door handle is an example of?', 'Pulley', 'Wheel and axle', 'Wedge', 'Lever', 1, 'Wheel and axle — rotational force', 'All'),
            ('eng', 'Best electrical insulator?', 'Copper', 'Iron', 'Rubber', 'Aluminium', 2, 'Rubber is a poor conductor', 'All'),
            ('eng', 'Mechanical advantage of a fixed pulley?', '1', '2', '0.5', '10', 0, 'Changes direction but not force', 'All'),
            ('eng', 'Main material in modern skyscraper frames?', 'Wood', 'Steel', 'Brick', 'Plastic', 1, 'Steel provides high strength', 'All'),
            ('eng', 'Triangles are used in trusses because?', 'They are pretty', 'They are rigid', 'They save space', 'They are cheap', 1, "Triangles don't deform under load", 'All'),
            ('eng', 'Unit of electrical resistance?', 'Volt', 'Ampere', 'Ohm', 'Watt', 2, 'Resistance is measured in Ohms (Ω)', 'All'),

            # Environment
            ('env', 'Primary cause of global warming?', 'Deforestation only', 'Greenhouse gas emissions', 'Volcanic eruptions', 'Ocean tides', 1, 'Greenhouse gases trap heat', 'All'),
            ('env', 'Which layer protects us from UV rays?', 'Oxygen layer', 'Ozone layer', 'Nitrogen layer', 'Carbon layer', 1, 'O₃ filters ultraviolet radiation', 'All'),
            ('env', 'Process of turning waste into new products?', 'Reuse', 'Recycle', 'Reduce', 'Compost', 1, 'Recycling processes materials', 'All'),
            ('env', 'Which gas is most abundant in Earth\'s atmosphere?', 'Oxygen', 'Nitrogen', 'Carbon Dioxide', 'Argon', 1, 'Nitrogen is ~78%', 'All'),
            ('env', 'Energy from the heat inside the Earth?', 'Solar', 'Geothermal', 'Wind', 'Hydroelectric', 1, 'Geo (Earth) + Thermal (Heat)', 'All'),
            ('env', 'Main source of ocean pollution?', 'Shipwrecks', 'Land-based runoff', 'Acid rain', 'Underwater volcanoes', 1, 'Most waste comes from land', 'All'),

            # Daily
            ('daily', 'Car accelerates 0→60 m/s in 12s. Acceleration?', '5 m/s²', '6 m/s²', '7.2 m/s²', '4 m/s²', 0, 'a=Δv/t=60/12=5 m/s²', 'All'),
            ('daily', 'If you have 3 apples and take away 2, how many do YOU have?', '1', '2', '3', '5', 1, 'You took 2, so you have 2!', 'All')
        ]
        cursor.executemany('''
            INSERT INTO questions (subject, question, opt_a, opt_b, opt_c, opt_d, answer_idx, explanation, class_name)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', default_questions)

    # Seed demo student if missing
    cursor.execute('SELECT COUNT(*) FROM students')
    if cursor.fetchone()[0] == 0:
        cursor.execute('''
            INSERT INTO students (name, username, password, xp, streak, level, class_name, state, math_score, science_score, tech_score, eng_score, env_score)
            VALUES ('Rahul Kumar', 'rahul', 'rahul123@', 1250, 7, 8, 'Class 8', 'Maharashtra', 85, 90, 75, 80, 70)
        ''')

    conn.commit()
    conn.close()

# Knowledge Base for AI Chatbot
STEM_KNOWLEDGE = {
    "photosynthesis": "Photosynthesis is how plants use sunlight, water, and CO2 to make food (glucose) and oxygen. It happens in chloroplasts!",
    "gravity": "Gravity is the force that pulls objects toward each other. On Earth, it pulls everything down toward the center at 9.8 m/s².",
    "newton": "Isaac Newton is famous for his three laws of motion and the law of universal gravitation.",
    "atom": "An atom is the smallest unit of matter, consisting of a nucleus (protons and neutrons) and orbiting electrons.",
    "energy": "Energy is the ability to do work. It comes in many forms: kinetic, potential, thermal, chemical, and more.",
    "dna": "DNA is the molecule that carries genetic instructions for all living things. It looks like a double helix!",
    "cell": "The cell is the basic structural and functional unit of life. All living things are made of cells!",
    "water": "Water (H2O) is essential for life. It exists in three states: solid (ice), liquid, and gas (vapor).",
    "electricity": "Electricity is the flow of electrons through a conductor like a copper wire.",
    "sun": "The Sun is a star at the center of our solar system. It provides energy to Earth through light and heat.",
    "volcano": "A volcano is a rupture in the crust of a planetary-mass object that allows hot lava, ash, and gases to escape.",
    "planet": "A planet is a large celestial body that orbits around a star like the Sun.",
    "pi": "Pi (π) is the ratio of a circle's circumference to its diameter, approximately equal to 3.14159.",
    "triangle": "A triangle is a polygon with three sides and three angles. The sum of its angles is always 180 degrees.",
    "algebra": "Algebra is a branch of mathematics where symbols and letters represent numbers in equations.",
    "geometry": "Geometry is the branch of math concerned with shapes, sizes, and properties of space.",
    "pythagoras": "The Pythagorean theorem states that in a right triangle, a² + b² = c².",
    "fraction": "A fraction represents a part of a whole, written as a numerator over a denominator.",
    "percentage": "Percentage is a ratio expressed as a fraction of 100 using the symbol %.",
    "democracy": "Democracy is a system of government where power is vested in the people who elect representatives.",
    "constitution": "A constitution is the fundamental set of principles according to which a nation is governed.",
    "gandhi": "Mahatma Gandhi led India's non-violent independence movement against British rule.",
    "himalayas": "The Himalayas are the highest mountain range in the world, home to Mount Everest."
}

# --- ROUTES ---

@app.route('/')
def serve_index():
    return send_from_directory('.', 'index.html')

@app.route('/api/auth/register', methods=['POST'])
def register():
    data = request.json or {}
    role = data.get('role', 'student')
    user = data.get('username', '').strip()
    password = data.get('password', '')

    if not user or not password:
        return jsonify({'success': False, 'message': 'Username and password required'}), 400

    conn = get_db()
    cursor = conn.cursor()

    try:
        if role == 'student':
            name = data.get('name', '').strip() or user
            class_name = data.get('class', 'Class 8')
            state = data.get('state', 'Maharashtra')
            cursor.execute('''
                INSERT INTO students (name, username, password, class_name, state)
                VALUES (?, ?, ?, ?, ?)
            ''', (name, user, password, class_name, state))
        elif role == 'teacher':
            school = data.get('school', '')
            cursor.execute('''
                INSERT INTO teachers (username, password, school)
                VALUES (?, ?, ?)
            ''', (user, password, school))
        elif role == 'parent':
            child_user = data.get('child_username', '').strip()
            relation = data.get('relation', 'Parent')
            cursor.execute('SELECT username FROM students WHERE username=?', (child_user,))
            if not cursor.fetchone():
                conn.close()
                return jsonify({'success': False, 'message': 'Linked child username not found'}), 404
            cursor.execute('''
                INSERT INTO parents (username, password, child_username, relation)
                VALUES (?, ?, ?, ?)
            ''', (user, password, child_user, relation))

        conn.commit()
        conn.close()
        return jsonify({'success': True, 'message': f'{role.capitalize()} registered successfully!'})
    except sqlite3.IntegrityError:
        conn.close()
        return jsonify({'success': False, 'message': 'Username already exists'}), 400

@app.route('/api/auth/login', methods=['POST'])
def login():
    data = request.json or {}
    role = data.get('role', 'student')
    user = data.get('username', '').strip()
    password = data.get('password', '')

    conn = get_db()
    cursor = conn.cursor()

    if role == 'student':
        cursor.execute('SELECT * FROM students WHERE username=? AND password=?', (user, password))
        row = cursor.fetchone()
        conn.close()
        if row:
            student = dict(row)
            student['subjects'] = {
                'math': student.pop('math_score', 0),
                'science': student.pop('science_score', 0),
                'tech': student.pop('tech_score', 0),
                'eng': student.pop('eng_score', 0),
                'env': student.pop('env_score', 0)
            }
            student['class'] = student.pop('class_name', 'Class 8')
            student['user'] = student['username']
            return jsonify({'success': True, 'user': student})
    elif role == 'teacher':
        cursor.execute('SELECT * FROM teachers WHERE username=? AND password=?', (user, password))
        row = cursor.fetchone()
        conn.close()
        if row:
            return jsonify({'success': True, 'user': dict(row)})
    elif role == 'parent':
        cursor.execute('SELECT * FROM parents WHERE username=? AND password=?', (user, password))
        p_row = cursor.fetchone()
        if p_row:
            p_dict = dict(p_row)
            cursor.execute('SELECT * FROM students WHERE username=?', (p_dict['child_username'],))
            c_row = cursor.fetchone()
            conn.close()
            if c_row:
                child = dict(c_row)
                child['subjects'] = {
                    'math': child.pop('math_score', 0),
                    'science': child.pop('science_score', 0),
                    'tech': child.pop('tech_score', 0),
                    'eng': child.pop('eng_score', 0),
                    'env': child.pop('env_score', 0)
                }
                child['class'] = child.pop('class_name', 'Class 8')
                child['user'] = child['username']
                return jsonify({'success': True, 'parent': p_dict, 'child': child})

    conn.close()
    return jsonify({'success': False, 'message': 'Invalid credentials'}), 401

@app.route('/api/student/<username>', methods=['GET'])
def get_student(username):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM students WHERE username=?', (username,))
    row = cursor.fetchone()
    conn.close()
    if row:
        student = dict(row)
        student['subjects'] = {
            'math': student.pop('math_score', 0),
            'science': student.pop('science_score', 0),
            'tech': student.pop('tech_score', 0),
            'eng': student.pop('eng_score', 0),
            'env': student.pop('env_score', 0)
        }
        student['class'] = student.pop('class_name', 'Class 8')
        student['user'] = student['username']
        return jsonify({'success': True, 'student': student})
    return jsonify({'success': False, 'message': 'Student not found'}), 404

@app.route('/api/student/update', methods=['POST'])
def update_student():
    data = request.json or {}
    username = data.get('username') or data.get('user')
    if not username:
        return jsonify({'success': False, 'message': 'Username required'}), 400

    conn = get_db()
    cursor = conn.cursor()

    xp = data.get('xp')
    level = data.get('level')
    streak = data.get('streak')
    subjects = data.get('subjects', {})

    fields = []
    params = []

    if xp is not None:
        fields.append('xp=?')
        params.append(xp)
    if level is not None:
        fields.append('level=?')
        params.append(level)
    if streak is not None:
        fields.append('streak=?')
        params.append(streak)

    if 'math' in subjects:
        fields.append('math_score=?'); params.append(subjects['math'])
    if 'science' in subjects:
        fields.append('science_score=?'); params.append(subjects['science'])
    if 'tech' in subjects:
        fields.append('tech_score=?'); params.append(subjects['tech'])
    if 'eng' in subjects:
        fields.append('eng_score=?'); params.append(subjects['eng'])
    if 'env' in subjects:
        fields.append('env_score=?'); params.append(subjects['env'])

    if fields:
        params.append(username)
        query = f"UPDATE students SET {', '.join(fields)} WHERE username=?"
        cursor.execute(query, params)
        conn.commit()

    conn.close()
    return jsonify({'success': True, 'message': 'Student updated successfully'})

@app.route('/api/leaderboard', methods=['GET'])
def leaderboard():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT username as user, name, xp, level, streak FROM students ORDER BY xp DESC LIMIT 10')
    rows = cursor.fetchall()
    conn.close()
    return jsonify({'success': True, 'leaderboard': [dict(r) for r in rows]})

@app.route('/api/questions', methods=['GET'])
def get_questions():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM questions')
    rows = cursor.fetchall()
    conn.close()

    result = {}
    for r in rows:
        q = dict(r)
        subj = q['subject']
        if subj not in result:
            result[subj] = []
        result[subj].append({
            'id': q['id'],
            'q': q['question'],
            'opts': [q['opt_a'], q['opt_b'], q['opt_c'], q['opt_d']],
            'ans': q['answer_idx'],
            'exp': q['explanation'],
            'cls': q['class_name']
        })

    return jsonify({'success': True, 'questions': result})

@app.route('/api/questions/add', methods=['POST'])
def add_question():
    data = request.json or {}
    subj = data.get('subject')
    q_text = data.get('question')
    opts = data.get('opts', [])
    ans = data.get('ans', 0)
    exp = data.get('exp', '')
    cls = data.get('class_name', 'All')

    if not subj or not q_text or len(opts) < 4:
        return jsonify({'success': False, 'message': 'Invalid question format'}), 400

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO questions (subject, question, opt_a, opt_b, opt_c, opt_d, answer_idx, explanation, class_name)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (subj, q_text, opts[0], opts[1], opts[2], opts[3], ans, exp, cls))
    conn.commit()
    conn.close()
    return jsonify({'success': True, 'message': 'Question added!'})

@app.route('/api/questions/<int:q_id>', methods=['DELETE'])
def delete_question(q_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM questions WHERE id=?', (q_id,))
    conn.commit()
    conn.close()
    return jsonify({'success': True, 'message': 'Question deleted'})

@app.route('/api/ai/chat', methods=['POST'])
def ai_chat():
    data = request.json or {}
    query = data.get('query', '').strip().lower()

    if not query:
        return jsonify({'response': "Hello! I'm your VidyaQuest AI. How can I help you in STEM today?"})

    # Basic math expression evaluator
    math_match = re.search(r'(\d+)\s*([\+\-\*\/])\s*(\d+)', query)
    if math_match:
        n1 = float(math_match.group(1))
        op = math_match.group(2)
        n2 = float(math_match.group(3))
        res = n1 + n2 if op == '+' else n1 - n2 if op == '-' else n1 * n2 if op == '*' else (round(n1/n2, 2) if n2 != 0 else 'infinity')
        return jsonify({'response': f"The answer to {n1} {op} {n2} is {res}."})

    # Match in Knowledge Base
    for key, val in STEM_KNOWLEDGE.items():
        if key in query:
            return jsonify({'response': val})

    return jsonify({'response': f"Great question about '{query}'! STEM concepts are all around us. Try asking specifically about gravity, photosynthesis, atoms, or algebra!"})

@app.route('/api/teacher/students', methods=['GET'])
def teacher_students():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM students')
    rows = cursor.fetchall()
    conn.close()

    result = []
    for r in rows:
        stu = dict(r)
        stu['subjects'] = {
            'math': stu.pop('math_score', 0),
            'science': stu.pop('science_score', 0),
            'tech': stu.pop('tech_score', 0),
            'eng': stu.pop('eng_score', 0),
            'env': stu.pop('env_score', 0)
        }
        stu['class'] = stu.pop('class_name', 'Class 8')
        stu['user'] = stu['username']
        result.append(stu)

    return jsonify({'success': True, 'students': result})

if __name__ == '__main__':
    init_db()
    print("[SERVER] VidyaQuest Python Server running on http://localhost:5000")
    app.run(host='0.0.0.0', port=5000, debug=True)
