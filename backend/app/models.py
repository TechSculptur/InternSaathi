from datetime import date

from sqlalchemy import Boolean, Column, Date, ForeignKey, Integer, String, Table, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


internship_skills = Table(
    "internship_skills",
    Base.metadata,
    Column("internship_id", String(32), ForeignKey("internships.id", ondelete="CASCADE"), primary_key=True),
    Column("skill_id", Integer, ForeignKey("skills.id", ondelete="CASCADE"), primary_key=True),
)

internship_educations = Table(
    "internship_educations",
    Base.metadata,
    Column("internship_id", String(32), ForeignKey("internships.id", ondelete="CASCADE"), primary_key=True),
    Column("education_id", Integer, ForeignKey("education_categories.id", ondelete="CASCADE"), primary_key=True),
)


class EducationCategory(Base):
    __tablename__ = "education_categories"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    code: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)
    label_en: Mapped[str] = mapped_column(String(100), nullable=False)
    label_hi: Mapped[str] = mapped_column(String(100), nullable=False)

    internships = relationship(
        "Internship",
        secondary="internship_educations",
        back_populates="accepted_educations",
    )


class Sector(Base):
    __tablename__ = "sectors"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    code: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)
    name_en: Mapped[str] = mapped_column(String(100), nullable=False)
    name_hi: Mapped[str] = mapped_column(String(100), nullable=False)

    internships = relationship("Internship", back_populates="sector")


class Skill(Base):
    __tablename__ = "skills"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    code: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)
    name_en: Mapped[str] = mapped_column(String(100), nullable=False)
    name_hi: Mapped[str] = mapped_column(String(100), nullable=False)
    sector_code: Mapped[str] = mapped_column(String(50), nullable=True)

    internships = relationship(
        "Internship",
        secondary=internship_skills,
        back_populates="required_skills",
    )


class Internship(Base):
    __tablename__ = "internships"

    id: Mapped[str] = mapped_column(String(32), primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    organization_name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    sector_id: Mapped[int] = mapped_column(Integer, ForeignKey("sectors.id"), nullable=False, index=True)
    state: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    district: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    work_mode: Mapped[str] = mapped_column(String(20), nullable=False)
    duration_months: Mapped[int] = mapped_column(Integer, nullable=False)
    stipend_inr: Mapped[int] = mapped_column(Integer, nullable=False)
    deadline: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False, index=True)
    allows_no_skills: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_sample: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    sector = relationship("Sector", back_populates="internships")
    required_skills = relationship(
        "Skill",
        secondary=internship_skills,
        back_populates="internships",
        lazy="selectin",
    )
    accepted_educations = relationship(
        "EducationCategory",
        secondary=internship_educations,
        back_populates="internships",
        lazy="selectin",
    )


__all__ = [
    "EducationCategory", "Sector", "Skill", "Internship",
    "internship_skills", "internship_educations",
]
