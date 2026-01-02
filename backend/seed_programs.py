#!/usr/bin/env python3
"""
Seed script for 30-day structured preparation programs.
Creates sample programs with days and tasks.

Run with: python seed_programs.py
"""

import os
import sys
from pathlib import Path

# Add the backend directory to Python path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

from app.db import get_db, init_db
from app.models import (
    Program, ProgramDay, ProgramDayTask, 
    ProgramDifficulty, ProgramTaskType
)
from sqlalchemy.orm import Session


def create_software_engineer_program(db: Session) -> Program:
    """Create the Software Engineer 30-day program."""
    
    # Create the program
    program = Program(
        slug="software-engineer-intermediate",
        title="30-Day Interview Prep: Software Engineer (Intermediate)",
        description="Comprehensive preparation program for mid-level software engineering roles. Covers data structures, algorithms, system design, and behavioral questions with daily practice sessions.",
        target_role="Software Engineer",
        difficulty=ProgramDifficulty.INTERMEDIATE,
        is_published=True
    )
    
    db.add(program)
    db.flush()  # Get the ID
    
    # Sample focus competencies for different types of days
    tech_competencies = ["Problem Solving", "Algorithms", "Data Structures"]
    system_competencies = ["System Design", "Architecture", "Scalability"]
    behavioral_competencies = ["Communication", "Teamwork", "Leadership"]
    coding_competencies = ["Coding", "Debugging", "Code Quality"]
    
    # Create 30 days with varied content
    days_data = [
        (1, "Welcome & Assessment", tech_competencies),
        (2, "Arrays & Strings Basics", tech_competencies),
        (3, "Linked Lists Fundamentals", tech_competencies),
        (4, "Behavioral - STAR Method", behavioral_competencies),
        (5, "Mock Interview: Arrays", tech_competencies),
        (6, "Stacks & Queues", tech_competencies),
        (7, "Hash Tables Deep Dive", tech_competencies),
        (8, "Trees & Binary Search", tech_competencies),
        (9, "Communication Skills", behavioral_competencies),
        (10, "Mock Interview: Trees", tech_competencies),
        (11, "Graph Algorithms", tech_competencies),
        (12, "Dynamic Programming Intro", tech_competencies),
        (13, "System Design Basics", system_competencies),
        (14, "Behavioral - Past Projects", behavioral_competencies),
        (15, "Mock Interview: Graphs", tech_competencies),
        (16, "Advanced DP Problems", tech_competencies),
        (17, "Database Design", system_competencies),
        (18, "API Design Principles", system_competencies),
        (19, "Code Quality & Testing", coding_competencies),
        (20, "Mock Interview: System Design", system_competencies),
        (21, "Concurrency & Threading", tech_competencies),
        (22, "Microservices Architecture", system_competencies),
        (23, "Behavioral - Challenges", behavioral_competencies),
        (24, "Performance Optimization", coding_competencies),
        (25, "Mock Interview: Mixed Topics", tech_competencies),
        (26, "Scalability Patterns", system_competencies),
        (27, "Final Review - Algorithms", tech_competencies),
        (28, "Final Review - System Design", system_competencies),
        (29, "Mock Interview - Final Prep", behavioral_competencies),
        (30, "Graduation & Next Steps", behavioral_competencies)
    ]
    
    for day_num, title, competencies in days_data:
        day = ProgramDay(
            program_id=program.id,
            day_number=day_num,
            title=title,
            focus_competencies=competencies
        )
        db.add(day)
        db.flush()
        
        # Create tasks for each day
        create_tasks_for_day(db, day, day_num)
    
    return program


def create_hr_manager_program(db: Session) -> Program:
    """Create the HR Manager 30-day program."""
    
    # Create the program
    program = Program(
        slug="hr-manager-advanced",
        title="30-Day Interview Prep: HR Manager (Advanced)",
        description="Advanced preparation program for senior HR management positions. Focus on strategic HR, leadership scenarios, compliance, and advanced behavioral interview techniques.",
        target_role="HR Manager",
        difficulty=ProgramDifficulty.ADVANCED,
        is_published=True
    )
    
    db.add(program)
    db.flush()
    
    # HR-specific competencies
    leadership_competencies = ["Leadership", "Team Management", "Strategic Thinking"]
    hr_competencies = ["HR Strategy", "Talent Management", "Employee Relations"]
    compliance_competencies = ["Legal Compliance", "Risk Management", "Policy Development"]
    communication_competencies = ["Communication", "Conflict Resolution", "Negotiation"]
    
    # Create 30 days for HR Manager program
    days_data = [
        (1, "HR Strategy Overview", hr_competencies),
        (2, "Talent Acquisition Deep Dive", hr_competencies),
        (3, "Employee Relations Basics", hr_competencies),
        (4, "Leadership Scenarios", leadership_competencies),
        (5, "Mock Interview: HR Strategy", hr_competencies),
        (6, "Performance Management", hr_competencies),
        (7, "Compensation & Benefits", hr_competencies),
        (8, "Legal Compliance Issues", compliance_competencies),
        (9, "Communication Excellence", communication_competencies),
        (10, "Mock Interview: Leadership", leadership_competencies),
        (11, "Change Management", leadership_competencies),
        (12, "Diversity & Inclusion", hr_competencies),
        (13, "HR Analytics & Metrics", hr_competencies),
        (14, "Conflict Resolution", communication_competencies),
        (15, "Mock Interview: Employee Relations", hr_competencies),
        (16, "Strategic HR Planning", hr_competencies),
        (17, "Labor Relations", compliance_competencies),
        (18, "Organizational Development", leadership_competencies),
        (19, "HR Technology Systems", hr_competencies),
        (20, "Mock Interview: Compliance", compliance_competencies),
        (21, "Crisis Management", leadership_competencies),
        (22, "Executive Coaching", leadership_competencies),
        (23, "Budget & Resource Management", leadership_competencies),
        (24, "Stakeholder Management", communication_competencies),
        (25, "Mock Interview: Strategic HR", hr_competencies),
        (26, "Future of Work Trends", hr_competencies),
        (27, "Final Review - Leadership", leadership_competencies),
        (28, "Final Review - HR Strategy", hr_competencies),
        (29, "Mock Interview - Executive Level", leadership_competencies),
        (30, "Career Advancement Planning", leadership_competencies)
    ]
    
    for day_num, title, competencies in days_data:
        day = ProgramDay(
            program_id=program.id,
            day_number=day_num,
            title=title,
            focus_competencies=competencies
        )
        db.add(day)
        db.flush()
        
        # Create tasks for each day
        create_tasks_for_day(db, day, day_num)
    
    return program


def create_tasks_for_day(db: Session, day: ProgramDay, day_num: int):
    """Create 2-4 tasks for a given day."""
    
    # Determine if this day should have a mock interview
    has_mock_interview = (day_num % 5 == 0 or day_num == 1 or day_num >= 25)
    
    tasks = []
    
    # Always start with a reading task
    tasks.append({
        "task_type": ProgramTaskType.READ,
        "title": f"Read: {day.title} Fundamentals",
        "details": f"Review key concepts and best practices for {day.title.lower()}. Study the provided materials and take notes on important points.",
        "meta": {"estimatedMinutes": 15},
        "sort_order": 1
    })
    
    # Add a practice task
    if "Mock Interview" not in day.title:
        tasks.append({
            "task_type": ProgramTaskType.PRACTICE,
            "title": f"Practice: {day.title} Exercises",
            "details": f"Complete hands-on exercises related to {day.title.lower()}. Practice applying the concepts you've learned.",
            "meta": {"exerciseCount": 3, "estimatedMinutes": 20},
            "sort_order": 2
        })
    
    # Add mock interview task for certain days
    if has_mock_interview:
        duration = 10 if day_num <= 15 else 15  # Longer interviews later in program
        tasks.append({
            "task_type": ProgramTaskType.MOCK_INTERVIEW,
            "title": f"Mock Interview: {day.title}",
            "details": f"Complete a focused mock interview session on {day.title.lower()} topics. Get AI feedback on your performance.",
            "meta": {
                "durationMin": duration,
                "questionStyle": "focused",
                "templateId": f"day_{day_num}_template",
                "questionCount": 3 if duration == 10 else 5
            },
            "sort_order": 3 if len(tasks) == 2 else 2
        })
    
    # Add reflection task
    tasks.append({
        "task_type": ProgramTaskType.REFLECTION,
        "title": "Daily Reflection",
        "details": "Reflect on what you learned today. Write down key insights and areas for improvement.",
        "meta": {"estimatedMinutes": 10},
        "sort_order": len(tasks) + 1
    })
    
    # Create task records
    for task_data in tasks:
        task = ProgramDayTask(
            program_day_id=day.id,
            task_type=task_data["task_type"],
            title=task_data["title"],
            details=task_data["details"],
            meta=task_data["meta"],
            sort_order=task_data["sort_order"]
        )
        db.add(task)


def seed_programs():
    """Main function to seed program data."""
    print("🌱 Seeding 30-day programs...")
    
    # Initialize database
    init_db()
    
    # Get database session
    db = next(get_db())
    
    try:
        # Check if programs already exist
        existing_programs = db.query(Program).filter(Program.is_published == True).count()
        if existing_programs > 0:
            print(f"⚠️  Found {existing_programs} existing published programs. Skipping seed.")
            return
        
        # Create programs
        print("Creating Software Engineer program...")
        se_program = create_software_engineer_program(db)
        
        print("Creating HR Manager program...")
        hr_program = create_hr_manager_program(db)
        
        # Commit all changes
        db.commit()
        
        print("✅ Successfully seeded programs:")
        print(f"   - {se_program.title} ({se_program.slug})")
        print(f"   - {hr_program.title} ({hr_program.slug})")
        
        # Print statistics
        se_days = db.query(ProgramDay).filter(ProgramDay.program_id == se_program.id).count()
        hr_days = db.query(ProgramDay).filter(ProgramDay.program_id == hr_program.id).count()
        
        se_tasks = db.query(ProgramDayTask).join(ProgramDay).filter(ProgramDay.program_id == se_program.id).count()
        hr_tasks = db.query(ProgramDayTask).join(ProgramDay).filter(ProgramDay.program_id == hr_program.id).count()
        
        print(f"📊 Statistics:")
        print(f"   - Software Engineer: {se_days} days, {se_tasks} tasks")
        print(f"   - HR Manager: {hr_days} days, {hr_tasks} tasks")
        
    except Exception as e:
        print(f"❌ Error seeding programs: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_programs()
