
import streamlit as st
import google.generativeai as genai
from streamlit_option_menu import option_menu
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from xml.sax.saxutils import escape
from datetime import datetime
import html

# -------------------------
# PAGE CONFIG
# -------------------------
st.set_page_config(
    page_title="AI Resume Builder",
    page_icon="🚀",
    layout="wide"
)

# -------------------------
# GEMINI
# -------------------------
genai.configure(
    api_key=st.secrets["GEMINI_API_KEY"]
)

model = genai.GenerativeModel(
    "gemini-2.5-flash"
)

# -------------------------
# STYLING
# -------------------------
st.markdown("""
<style>

.stApp{

background:linear-gradient(
135deg,
#090979,
#3f37c9,
#7209b7,
#00b4d8
);

background-size:400% 400%;
animation:gradient 12s infinite;
overflow:hidden;
}

@keyframes gradient{

0%{
background-position:0% 50%;
}

50%{
background-position:100% 50%;
}

100%{
background-position:0% 50%;
}
}


/* floating circles */

.float1{
position:fixed;
top:10%;
left:8%;
width:120px;
height:120px;
background:rgba(255,255,255,.12);
border-radius:50%;
animation:move1 8s infinite;
}

.float2{
position:fixed;
top:65%;
right:8%;
width:160px;
height:160px;
background:rgba(0,255,255,.15);
border-radius:50%;
animation:move2 10s infinite;
}

.float3{
position:fixed;
bottom:15%;
left:40%;
width:90px;
height:90px;
background:rgba(255,0,255,.15);
border-radius:50%;
animation:move3 6s infinite;
}

@keyframes move1{
50%{transform:translateY(50px)}
}

@keyframes move2{
50%{transform:translateX(-60px)}
}

@keyframes move3{
50%{
transform:
translateY(-50px)
translateX(40px)
}
}

.glass{

background:rgba(
255,
255,
255,
0.08
);

backdrop-filter:blur(15px);

padding:25px;

border-radius:20px;

border:1px solid rgba(
255,
255,
255,
0.2
);

box-shadow:
0px 10px 30px rgba(
0,
0,
0,
0.25
);

}

h1,h2,h3,p,label{
color:white !important;
}

</style>

<div class='float1'></div>
<div class='float2'></div>
<div class='float3'></div>

""",unsafe_allow_html=True)

# -------------------------
# SESSION
# -------------------------

defaults={

"logged_in":False,
"username":"",
"history":[]

}

for k,v in defaults.items():

    if k not in st.session_state:
        st.session_state[k]=v


# -------------------------
# LOGIN
# -------------------------

def login():

    c1,c2,c3=st.columns([1,2,1])

    with c2:

        st.markdown("""
        <div class='glass'>
        <h1 align='center'>
        🚀 AI Resume Builder
        </h1>
        </div>
        """,unsafe_allow_html=True)

        user=st.text_input(
        "Username"
        )

        pwd=st.text_input(
        "Password",
        type="password"
        )

        if st.button(
        "Login",
        use_container_width=True
        ):

            if user and pwd:

                st.session_state.logged_in=True
                st.session_state.username=user

                st.rerun()

            else:

                st.warning(
                "Enter details"
                )


if not st.session_state.logged_in:

    login()
    st.stop()

# -------------------------
# TOP NAVIGATION
# -------------------------

selected=option_menu(

menu_title=None,

options=[

"Resume Builder",
"Portfolio",
"History",
"About"

],

icons=[

"file-earmark",
"globe",
"clock-history",
"info-circle"

],

orientation="horizontal",

styles={

"container":{
"background-color":"rgba(255,255,255,.1)"
},

"nav-link":{

"font-size":"16px",
"text-align":"center",
"color":"white"
},

"nav-link-selected":{

"background-color":"#00b4d8"

}

}

)

st.write(
f"👋 Welcome {st.session_state.username}"
)

# -------------------------
# PDF
# -------------------------

def pdf_create(text):

    file="resume.pdf"

    doc=SimpleDocTemplate(
    file
    )

    styles=getSampleStyleSheet()

    story=[

    Paragraph(
    "AI Resume",
    styles["Title"]
    ),

    Spacer(1,12),

    Paragraph(
    escape(
    text
    ).replace(
    "\n",
    "<br/>"
    ),

    styles["BodyText"]

    )
    ]

    doc.build(
    story
    )

    return file




# -------------------------
# RESUME PAGE
# -------------------------


if selected=="Resume Builder":

    st.markdown(
        "<div class='glass'>",
        unsafe_allow_html=True
    )

    st.title("📄 Resume Builder")

    name = st.text_input("Name")
    email = st.text_input("Email")
    skills = st.text_area("Skills")
    projects = st.text_area("Projects")

    if st.button("Generate Resume"):

        prompt = f"""
Generate ATS-friendly resume

Name: {name}
Email: {email}
Skills: {skills}
Projects: {projects}
"""

        from google.api_core.exceptions import ResourceExhausted
        import time

        resume = None

        for attempt in range(5):

            try:

                with st.spinner("Generating Resume..."):

                    response = model.generate_content(
                        prompt
                    )

                    resume = response.text

                break

            except ResourceExhausted:

                time.sleep(5)

        if resume:

    st.success("Resume generated successfully!")

else:

    # Backup resume if Gemini fails
    resume = f"""
# {name}

Email: {email}

## Skills
{skills}

## Projects
{projects}

## Profile Summary
Motivated candidate with skills in {skills}.
Seeking opportunities to apply knowledge and contribute effectively.
"""

st.write(resume)

st.session_state.history.append({

    "resume": resume,
    "date": datetime.now()

})

pdf = pdf_create(resume)

with open(pdf, "rb") as f:

    st.download_button(
        "📥 Download PDF",
        f,
        file_name="resume.pdf"
    )
    st.markdown(
        "</div>",
        unsafe_allow_html=True
    )

# -------------------------
# PORTFOLIO BUILDER
# -------------------------

elif selected=="Portfolio":

    st.title("🌐 AI Portfolio Builder")

    col1,col2=st.columns(2)

    with col1:

        name=st.text_input(
        "Name",
        key="p_name"
        )

        role=st.text_input(
        "Role",
        key="p_role"
        )

        about=st.text_area(
        "About You",
        key="p_about"
        )

        skills=st.text_area(
        "Skills (comma separated)",
        key="p_skills"
        )

        projects=st.text_area(
        "Projects",
        key="p_projects"
        )

        github=st.text_input(
        "GitHub Link"
        )

        linkedin=st.text_input(
        "LinkedIn Link"
        )

    with col2:

        st.subheader("Live Preview")

        html_content=f"""

        <html>

        <body style='
        font-family:Arial;
        background:linear-gradient(
        135deg,
        #1e1e2f,
        #2d1b69,
        #11998e
        );

        color:white;
        padding:40px;
        border-radius:20px;
        '>

        <center>

        <img src="https://cdn-icons-png.flaticon.com/512/3135/3135715.png"
        width="120">

        <h1>{html.escape(name)}</h1>

        <h3>{html.escape(role)}</h3>

        </center>

        <hr>

        <h2>👨 About</h2>

        <p>
        {html.escape(about)}
        </p>

        <h2>🛠 Skills</h2>

        <p>
        {html.escape(skills)}
        </p>

        <h2>🚀 Projects</h2>

        <p>
        {html.escape(projects)}
        </p>

        <h2>🔗 Connect</h2>

        <p>
        GitHub:
        <a href="{github}" style="color:cyan;">
        {github}
        </a>
        </p>

        <p>
        LinkedIn:
        <a href="{linkedin}" style="color:cyan;">
        {linkedin}
        </a>
        </p>

        </body>

        </html>

        """

        st.components.v1.html(
        html_content,
        height=700,
        scrolling=True
        )

        st.download_button(
        "📥 Download Portfolio HTML",
        html_content,
        file_name="portfolio.html",
        mime="text/html"
        )



# -------------------------
# HISTORY
# -------------------------

elif selected=="History":

    st.title(
    "📚 Resume History"
    )

    for item in reversed(
    st.session_state.history
    ):

        with st.expander(
        str(item["date"])
        ):

            st.write(
            item["resume"]
            )



# -------------------------
# ABOUT
# -------------------------

else:

    st.title("🚀 About The Project")

    st.markdown("""

# AI Resume & Portfolio Builder

### Project Overview

The AI Resume & Portfolio Builder is an intelligent web-based application developed to simplify and modernize the process of creating professional resumes and personal portfolios. The system leverages Artificial Intelligence to automatically generate ATS-friendly resumes and interactive portfolio pages, reducing manual effort while improving presentation quality and professional standards.

This application is designed to help students, fresh graduates, and professionals build strong digital profiles quickly and efficiently. The platform provides an intuitive and visually attractive user interface with modern animations and responsive design elements to enhance user experience.

---

### Objectives of the Project

The main objectives of this project are:

• To automate resume generation using Artificial Intelligence.

• To create resumes optimized for Applicant Tracking Systems (ATS).

• To generate professional portfolio pages dynamically.

• To provide an attractive and interactive user interface.

• To simplify profile creation and reduce manual formatting effort.

• To maintain generated resume history for future reference.

---

### Key Features

#### AI Resume Generation
The system uses Generative AI technology to create structured and professional resumes based on user input.

#### ATS Resume Analysis
Generated resumes are analyzed for ATS compatibility, including skill relevance, strengths, missing skills, and improvement suggestions.

#### Portfolio Builder
Users can create personalized portfolio pages containing profile information, projects, skills, and professional links.

#### PDF Export Functionality
Users can download generated resumes as PDF documents for easy sharing and professional use.

#### Resume History Tracking
The application maintains previously generated resumes within the session for future access.

#### Interactive User Interface
The application includes modern UI components such as:

- Animated backgrounds
- Floating visual elements
- Glassmorphism design
- Responsive layouts
- Dynamic navigation

---

### Technologies Used

**Frontend:**

• Streamlit

**Programming Language:**

• Python

**Artificial Intelligence Model:**

• Google Gemini AI

**Libraries Used:**

• ReportLab  
• HTML/CSS  
• Streamlit Components  
• Datetime  

---

### Benefits of the Project

• Reduces time required to build resumes.

• Improves resume quality and ATS performance.

• Helps users create professional online presence.

• Provides a user-friendly and visually appealing interface.

• Enhances productivity through AI automation.

---

### Future Enhancements

The project can be further enhanced by implementing:

• Database integration for permanent user storage

• User authentication system

• Multiple resume templates

• LinkedIn profile import

• Dark and Light mode switching

• Advanced analytics dashboard

• Cloud deployment support

---

### Conclusion

The AI Resume & Portfolio Builder demonstrates how Artificial Intelligence can improve traditional resume creation processes by introducing automation, intelligent recommendations, and modern user experience design. The system provides users with an efficient, professional, and visually engaging platform for building digital profiles suitable for today's competitive environment.

""")

