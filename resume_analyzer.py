"""
Resume Analyzer Agent
Provides brutal, honest feedback on resume quality BEFORE the interview starts.
Identifies loopholes, red flags, ATS issues, and improvement areas.
"""

from typing import Dict
from langchain_core.messages import HumanMessage
import json


class ResumeAnalyzerAgent:
    """
    Pre-Interview Resume Judge
    Evaluates resume quality with brutal honesty:
    - ATS compatibility (will it pass automated screening?)
    - Red flags (gaps, job hopping, vague descriptions)
    - Formatting issues
    - Content quality (quantifiable achievements vs fluff)
    - Missing critical elements
    - Company fit analysis (uses Researcher Agent)
    """
    
    def __init__(self, llm, researcher_agent=None):
        self.llm = llm
        self.researcher = researcher_agent
    
    def analyze(self, resume_text: str, job_description: str = "", company_name: str = "") -> Dict:
        """
        Deep resume analysis with actionable feedback.
        Now includes company-specific insights using Researcher Agent.
        
        Returns:
            Dictionary with:
            - overall_grade: A-F
            - ats_score: 0-100 (will it pass automated screening?)
            - red_flags: List of concerning elements
            - strengths: What's working well
            - fatal_flaws: Deal-breakers
            - improvement_tips: Specific actionable fixes
            - section_scores: Breakdown by resume section
            - company_fit: How well candidate matches company expectations
            - company_gaps: What company expects but resume lacks
        """
        print("\n" + "📄"*40)
        print(" "*30 + "RESUME ANALYSIS")
        print("📄"*40 + "\n")
        
        print(f"   📄 ResumeAnalyzer: Processing {len(resume_text)} char resume...")
        
        # Fetch company expectations if company provided
        company_intel = ""
        company_expectations = ""
        if company_name and self.researcher:
            print(f"   📄 ResumeAnalyzer: Fetching {company_name} expectations via Researcher...")
            try:
                research_state = {
                    'company_name': company_name
                }
                result = self.researcher.run(research_state)
                company_intel = result.get('company_intel', '')
                
                if company_intel:
                    print(f"   📄 ResumeAnalyzer: Got {len(company_intel)} chars of company intel")
                    company_expectations = f"\n\nCOMPANY EXPECTATIONS:\n{company_intel}\n\nIMPORTANT: Evaluate if this resume matches what {company_name} typically looks for. Does the candidate's experience align with their culture and technical standards?"
                else:
                    print(f"   ⚠️ ResumeAnalyzer: No company intel received")
            except Exception as e:
                print(f"   ⚠️ ResumeAnalyzer: Company research failed: {e}")
        
        # Build comprehensive analysis prompt
        jd_context = f"\n\nTARGET JOB:\n{job_description}\n\nAnalyze resume fit for THIS SPECIFIC ROLE." if job_description else ""
        
        prompt = f"""You are a brutal but fair resume critic with 20 years of hiring experience.
Your job: Find EVERY problem in this resume. Be ruthlessly honest.

RESUME:
{resume_text}
{jd_context}
{company_expectations}

Analyze these dimensions:

1. **ATS COMPATIBILITY** (0-100 score)
   - Does it use keywords from job description?
   - Is formatting ATS-friendly (no tables, columns, graphics)?
   - Are job titles standard (not quirky/creative)?
   - Score explanation

2. **RED FLAGS** (List every suspicious element)
   - Employment gaps (>6 months unexplained)
   - Job hopping (3+ jobs in 2 years)
   - Vague descriptions ("Worked on various projects")
   - Lack of quantifiable achievements
   - Skills listed but not demonstrated
   - Typos, grammar errors
   - Unprofessional email/formatting
   - Buzzword overload without substance

3. **FATAL FLAWS** (Deal-breakers)
   - Missing critical sections (work experience, education)
   - No measurable achievements (all duties, no results)
   - Irrelevant experience (90%+ unrelated to target job)
   - Lies/exaggerations that can be caught
   - Too long (>2 pages) or too short (<1 page for experienced)

4. **STRENGTHS** (What's actually good)
   - Strong action verbs
   - Quantified achievements (X% improvement, $Y saved, Z users)
   - Clear progression (junior → mid → senior)
   - Relevant certifications/education
   - Notable companies/projects

5. **SECTION BREAKDOWN** (Score each 0-10)
   - Contact Info: Complete? Professional email?
   - Summary/Objective: Compelling? Or generic fluff?
   - Work Experience: Achievements or duties? Quantified?
   - Skills: Demonstrated or just listed?
   - Education: Relevant? Well-presented?
   - Projects (if any): Substantial or filler?

6. **IMPROVEMENT TIPS** (Top 5 specific fixes)
   - Not generic advice like "add more keywords"
   - Specific: "Change 'Responsible for database management' to 'Optimized PostgreSQL queries, reducing load time by 40% for 2M+ users'"

7. **COMPANY FIT ANALYSIS** (If company provided)
   - Match Level: Poor/Fair/Good/Excellent
   - What {company_name} expects: Technical depth, culture fit, experience level
   - What resume shows: Does it align?
   - Company-specific gaps: What's missing that {company_name} values
   - Tailoring suggestions: How to customize resume for THIS company

8. **OVERALL GRADE** (A/B/C/D/F)
   - A: Would get interview 90%+ of time
   - B: Solid, minor improvements needed
   - C: Needs significant work
   - D: Major overhaul required
   - F: Start from scratch

Return ONLY valid JSON:
{{
  "overall_grade": "C",
  "ats_score": 65,
  "red_flags": ["Gap from Jan 2023 - Aug 2023 unexplained", "Job hopping: 4 companies in 3 years"],
  "fatal_flaws": ["No quantified achievements - all duties", "90% of experience unrelated to target role"],
  "strengths": ["Good progression from junior to senior", "Strong technical skills listed"],
  "section_scores": {{
    "contact_info": 9,
    "summary": 4,
    "work_experience": 5,
    "skills": 6,
    "education": 8,
    "projects": 0
  }},
  "company_fit": {{
    "match_level": "Fair",
    "company_expects": "Google values scalability, distributed systems expertise, and proven impact at scale",
    "resume_shows": "Some backend experience but no mention of scale (millions of users, distributed systems)",
    "company_gaps": ["No distributed systems experience", "No mentions of scale/performance optimization", "Missing Google-valued skills: Kubernetes, gRPC"],
    "tailoring_tips": ["Add metrics showing scale (X million requests/day)", "Highlight any distributed systems work", "Mention collaboration on large codebases"]
  }},
  "improvement_tips": [
    "Add numbers to every achievement. 'Led team' → 'Led team of 5 engineers, shipped product to 100K users'",
    "Explain 8-month gap in 2023 (consulting? learning? sabbatical?)",
    "Remove generic buzzwords: 'team player', 'hard worker', 'passionate' - show don't tell",
    "Tailor skills section: You list Python but job needs AWS - add cloud experience or remove",
    "Add a projects section with GitHub links showing actual code"
  ],
  "detailed_feedback": "This resume reads like a job duties checklist, not a results showcase. Hiring managers spend 6 seconds scanning - yours doesn't grab attention..."
}}

CRITICAL: Return ONLY valid JSON. No markdown, no code blocks."""
        
        print(f"   📄 ResumeAnalyzer: Calling LLM for deep analysis...")
        response = self.llm.invoke([HumanMessage(content=prompt)])
        print(f"   📄 ResumeAnalyzer: Received {len(response.content)} chars")
        
        # Parse response
        raw_content = response.content.strip()
        
        # Remove markdown code blocks if present
        if raw_content.startswith('```'):
            lines = raw_content.split('\n')
            raw_content = '\n'.join(lines[1:-1]) if len(lines) > 2 else raw_content
            raw_content = raw_content.replace('```json', '').replace('```', '').strip()
        
        try:
            analysis = json.loads(raw_content)
            print(f"   📄 ResumeAnalyzer: ✅ Successfully parsed analysis")
            
            # Print summary
            print(f"\n   📊 RESUME VERDICT:")
            print(f"      Grade: {analysis.get('overall_grade', 'N/A')}")
            print(f"      ATS Score: {analysis.get('ats_score', 0)}/100")
            print(f"      Red Flags: {len(analysis.get('red_flags', []))}")
            print(f"      Fatal Flaws: {len(analysis.get('fatal_flaws', []))}")
            
            return analysis
            
        except Exception as e:
            print(f"   ❌ ResumeAnalyzer: JSON parsing failed")
            print(f"   ❌ Error: {str(e)}")
            print(f"   ❌ Raw response:\n{raw_content[:500]}")
            
            # Return structured error instead of crashing
            return {
                'overall_grade': 'F',
                'ats_score': 0,
                'red_flags': ['Analysis failed - resume may be unparseable'],
                'fatal_flaws': ['Resume could not be analyzed properly'],
                'strengths': [],
                'section_scores': {},
                'improvement_tips': ['Ensure resume is plain text, not scanned image'],
                'detailed_feedback': f'Analysis error: {str(e)}',
                'error': True
            }
    
    def generate_report(self, analysis: Dict) -> str:
        """
        Generate a formatted report for display in UI.
        """
        grade = analysis.get('overall_grade', 'F')
        ats_score = analysis.get('ats_score', 0)
        
        # Determine grade color
        grade_emoji = {
            'A': '🌟', 'B': '✅', 'C': '⚠️', 'D': '❌', 'F': '🚨'
        }.get(grade, '❓')
        
        report = f"""# {grade_emoji} Resume Analysis Report

## Overall Grade: **{grade}**
## ATS Compatibility Score: **{ats_score}/100**

"""
        
        # Company Fit Analysis (NEW - most important for tailoring)
        company_fit = analysis.get('company_fit', {})
        if company_fit and company_fit.get('match_level'):
            match_level = company_fit.get('match_level', 'Unknown')
            match_emoji = {
                'Excellent': '🌟', 'Good': '✅', 'Fair': '⚠️', 'Poor': '❌'
            }.get(match_level, '❓')
            
            report += f"### {match_emoji} COMPANY FIT: **{match_level}**\n\n"
            report += f"**What the company expects:**\n{company_fit.get('company_expects', 'N/A')}\n\n"
            report += f"**What your resume shows:**\n{company_fit.get('resume_shows', 'N/A')}\n\n"
            
            company_gaps = company_fit.get('company_gaps', [])
            if company_gaps:
                report += "**Critical gaps for this company:**\n"
                for gap in company_gaps:
                    report += f"- ❌ {gap}\n"
                report += "\n"
            
            tailoring_tips = company_fit.get('tailoring_tips', [])
            if tailoring_tips:
                report += "**How to tailor for this company:**\n"
                for tip in tailoring_tips:
                    report += f"- 💡 {tip}\n"
                report += "\n"
            
            report += "---\n\n"
        
        # Fatal Flaws (most important)
        fatal_flaws = analysis.get('fatal_flaws', [])
        if fatal_flaws:
            report += "### 🚨 FATAL FLAWS (Fix These First)\n\n"
            for flaw in fatal_flaws:
                report += f"- **{flaw}**\n"
            report += "\n"
        
        # Red Flags
        red_flags = analysis.get('red_flags', [])
        if red_flags:
            report += "### ⚠️ RED FLAGS\n\n"
            for flag in red_flags:
                report += f"- {flag}\n"
            report += "\n"
        
        # Strengths
        strengths = analysis.get('strengths', [])
        if strengths:
            report += "### ✅ STRENGTHS (Keep These)\n\n"
            for strength in strengths:
                report += f"- {strength}\n"
            report += "\n"
        
        # Section Breakdown
        section_scores = analysis.get('section_scores', {})
        if section_scores:
            report += "### 📊 SECTION SCORES\n\n"
            for section, score in section_scores.items():
                score_bar = "█" * score + "░" * (10 - score)
                report += f"**{section.replace('_', ' ').title()}**: {score_bar} {score}/10\n"
            report += "\n"
        
        # Improvement Tips
        tips = analysis.get('improvement_tips', [])
        if tips:
            report += "### 💡 TOP IMPROVEMENTS TO MAKE\n\n"
            for i, tip in enumerate(tips, 1):
                report += f"{i}. {tip}\n\n"
        
        # Detailed Feedback
        detailed = analysis.get('detailed_feedback', '')
        if detailed:
            report += f"### 📝 DETAILED ANALYSIS\n\n{detailed}\n"
        
        return report


# Initialize with Gemini Flash (fast and accurate) + Researcher for company intel
def create_resume_analyzer():
    """Factory function to create resume analyzer with configured LLM and researcher."""
    try:
        from agents import gemini_flash_model, GeminiWrapper, ResearcherAgent
        
        # Create LLM wrapper
        if not gemini_flash_model:
            print("⚠️ Gemini Flash not available")
            return None
        
        llm = GeminiWrapper(gemini_flash_model, temperature=0.3)
        
        # Create researcher agent for company intelligence
        # ResearcherAgent initializes its own tavily_client internally
        try:
            researcher = ResearcherAgent()
            print("✅ Resume Analyzer initialized with Researcher Agent")
        except Exception as e:
            researcher = None
            print(f"⚠️ Tavily not available - company fit analysis will be limited: {e}")
        
        return ResumeAnalyzerAgent(llm, researcher_agent=researcher)
        
    except Exception as e:
        print(f"⚠️ Resume analyzer initialization failed: {e}")
        return None
