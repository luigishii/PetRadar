from sqlalchemy import Boolean, TIMESTAMP, DECIMAL, Integer, String, Text, Column, UUID, DateTime, ForeignKey, CheckConstraint
from sqlalchemy.orm import relationship
from src.models.base import Base
from sqlalchemy.schema import UniqueConstraint


class AvailabilityPeriod(Base):
    __tablename__ = "availability_period"

    id = Column(UUID, primary_key=True, index=True)
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=False)
    week_day_id = Column(UUID, ForeignKey("week_day.id"), nullable=False)
    veterinarian_id = Column(UUID, ForeignKey("veterinarian.id"), nullable=False)

    __table_args__ = (
        CheckConstraint("start_time <= end_time", name="check_start_before_end"),
    )

    week_day = relationship("WeekDay")
    veterinarian = relationship("Veterinarian")
    
    
class DonationDetails(Base):
    __tablename__ = "donation_details"
    __table_args__ = {'extend_existing': True}  # Permite redefinir a tabela caso já exista

    id = Column(UUID, primary_key=True, index=True)
    donation_type = Column(UUID, ForeignKey("donation_type.id"), nullable=False)
    status = Column(String(50), nullable=False)
    request_description = Column(Text, nullable=False)
    donation_link = Column(Text, nullable=False)
    pix = Column(Text, nullable=True)
    donation_amount = Column(DECIMAL, nullable=True)
    donation_item_quantity = Column(Integer, nullable=True)
    expire_at = Column(DateTime, nullable=False)
    created_at = Column(DateTime, nullable=False, default="NOW()")
    updated_at = Column(DateTime, nullable=True)

    __table_args__ = (
        CheckConstraint("donation_amount > 0", name="check_donation_amount_positive"),
    )

    donation_type_rel = relationship("DonationType")

    

    
class Location(Base):
    __tablename__ = "location"

    id = Column(UUID, primary_key=True, index=True)
    cep = Column(String(10), nullable=True)
    street = Column(String(150), nullable=True)
    neighborhood = Column(String(80), nullable=True)
    latitude = Column(DECIMAL(9,6), nullable=False)
    longitude = Column(DECIMAL(9,6), nullable=False)
    extra_info = Column(Text, nullable=True)
    created_at = Column(DateTime, nullable=False, default="NOW()")
    updated_at = Column(DateTime, nullable=True)

    __table_args__ = (
        CheckConstraint("street IS NULL OR street ~ '^[A-Za-zÀ-ÖØ-öø-ÿ\\s]+$'", name="chk_street_valid"),
        CheckConstraint("neighborhood IS NULL OR neighborhood ~ '^[A-Za-zÀ-ÖØ-öø-ÿ\\s]+$'", name="chk_neighborhood_valid"),
    )
    

class Ong(Base):
    __tablename__ = "ong"

    id = Column(UUID, primary_key=True, index=True)
    location_id = Column(UUID, ForeignKey("location.id"), nullable=False)
    cnpj = Column(String(18), nullable=False)
    description = Column(Text, nullable=True)
    foundation_date = Column(DateTime, nullable=True)
    activity_area = Column(String(50), nullable=True)
    legal_representative = Column(String(50), nullable=True)
    website_url = Column(Text, nullable=True)
    legal_registration_date = Column(DateTime, nullable=False, default="NOW()")
    status = Column(String(10), nullable=False)

    __table_args__ = (
        CheckConstraint("status IN ('ACTIVE', 'INACTIVE')", name="chk_status_valid"),
        CheckConstraint("cnpj ~ '^\\d{2}\\.\\d{3}\\.\\d{3}/\\d{4}-\\d{2}$'", name="chk_cnpj_format"),
        CheckConstraint("legal_representative IS NULL OR legal_representative ~ '^[A-Za-zÀ-ÖØ-öø-ÿ\\s]+$'", name="chk_legal_rep_name"),
        CheckConstraint("foundation_date IS NULL OR foundation_date <= NOW()", name="chk_foundation_date"),
    )

    location = relationship("Location")
    

class Pet(Base):
    __tablename__ = "pet"

    id = Column(UUID, primary_key=True, index=True)
    owner_id = Column(UUID, ForeignKey("user.id"), nullable=False)
    name = Column(String(50), nullable=False)
    pet_type = Column(String(50), nullable=False)
    size = Column(String(50), nullable=False)
    health_status = Column(String(50), nullable=False)
    found_at = Column(DateTime, nullable=True)
    updated_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, nullable=False, default="NOW()")
    breed_type_id = Column(UUID, ForeignKey("breed_type.id"), nullable=False)
    size_type_id = Column(UUID, ForeignKey("size_type.id"), nullable=False)

    owner = relationship("User")
    breed_type = relationship("BreedType")
    size_type = relationship("SizeType")
    

class Veterinarian(Base):
    __tablename__ = "veterinarian"

    id = Column(UUID, primary_key=True, index=True)
    location_id = Column(UUID, ForeignKey("location.id"), nullable=False)
    veterinarian_specialty_id = Column(UUID, ForeignKey("veterinarian_specialty.id"), nullable=False)
    veterinarian_qualification_id = Column(UUID, ForeignKey("veterinarian_qualification.id"), nullable=False)
    status = Column(String(15), nullable=False, default='ACTIVE')
    registration_number = Column(String(30), nullable=True)
    bio = Column(Text, nullable=True)
    created_at = Column(DateTime, nullable=False, default="NOW()")
    updated_at = Column(DateTime, nullable=True)

    __table_args__ = (
        CheckConstraint("status IN ('ACTIVE', 'INACTIVE')", name="chk_vet_status"),
    )

    location = relationship("Location")
    specialty = relationship("VeterinarianSpecialty")
    qualification = relationship("VeterinarianQualification")
    

class WeekDay(Base):
    __tablename__ = "week_day"

    id = Column(UUID, primary_key=True, index=True)
    name = Column(String(50), nullable=False, unique=True)

    __table_args__ = (
        CheckConstraint("name IN ('Domingo', 'Segunda-feira', 'Terça-feira', 'Quarta-feira', 'Quinta-feira', 'Sexta-feira', 'Sábado')", name="chk_week_day_name"),
    )

class NetworkTypes(Base):
    __tablename__ = "network_types"

    id = Column(UUID, primary_key=True, index=True)
    type_name = Column(String(50), nullable=False)

    __table_args__ = (
        CheckConstraint("type_name ~ '^[A-Za-zÀ-ÖØ-öø-ÿ\\s]+$'", name="chk_network_type_name"),
    )


class SocialNetwork(Base):
    __tablename__ = "social_networks"

    id = Column(UUID, primary_key=True, index=True)
    network_name = Column(String(50), nullable=False)
    network_url = Column(Text, nullable=False)
    network_type_id = Column(UUID, ForeignKey("network_types.id"), nullable=True)
    social_network_owner_id = Column(UUID, ForeignKey("user.id"), nullable=False)

    __table_args__ = (
        CheckConstraint("network_name ~ '^[A-Za-zÀ-ÖØ-öø-ÿ\\s]+$'", name="chk_network_name_format"),
    )

    # Relacionamentos
    network_type = relationship("NetworkType", backref="social_networks", cascade="all, delete-orphan")
    social_network_owner = relationship("User", backref="social_networks")
    

class User(Base):
    __tablename__ = "user"

    id = Column(UUID, primary_key=True, index=True)
    name = Column(String(50), nullable=False)
    last_name = Column(String(50), nullable=True)
    username = Column(String(50), nullable=False, unique=True)
    email = Column(String(255), nullable=False, unique=True)
    photo_url = Column(Text, nullable=True)
    password_hash = Column(Text, nullable=False)
    status = Column(String(50), nullable=False)
    phone = Column(String(15), nullable=False)
    work_phone = Column(String(15), nullable=True)
    work_email = Column(String(255), nullable=True)
    created_at = Column(DateTime, nullable=False, default="NOW()")
    updated_at = Column(DateTime, nullable=True)

    __table_args__ = (
        CheckConstraint("name ~ '^[A-Za-zÀ-ÖØ-öø-ÿ\\s]+$'", name="chk_name_format"),
        CheckConstraint("last_name IS NULL OR last_name ~ '^[A-Za-zÀ-ÖØ-öø-ÿ\\s]+$'", name="chk_last_name_format"),
        CheckConstraint("email ~ '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\\.[A-Za-z]{2,}$'", name="chk_email_format"),
        CheckConstraint("work_email IS NULL OR work_email ~* '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\\.[A-Za-z]{2,}$'", name="chk_work_email_format"),
        CheckConstraint("phone ~ '^\\(\\d{2}\\) \\d{5}-\\d{4}$'", name="chk_phone_format"),
        CheckConstraint("work_phone IS NULL OR work_phone ~ '^\\(\\d{2}\\) \\d{4,5}-\\d{4}$'", name="chk_work_phone_format"),
    )
    

class DonationType(Base):
    __tablename__ = "donation_type"

    id = Column(UUID, primary_key=True, index=True)
    name = Column(String(50), nullable=False)
    

class DonationDetail(Base):
    __tablename__ = "donation_detail"

    id = Column(UUID, primary_key=True, index=True)
    donation_type = Column(UUID, nullable=False)
    status = Column(String(50), nullable=False)
    request_description = Column(Text, nullable=False)
    donation_link = Column(Text, nullable=False)
    pix = Column(Text, nullable=True)
    donation_amount = Column(DECIMAL, nullable=True)
    donation_item_quantity = Column(Integer, nullable=True)
    expire_at = Column(DateTime, nullable=False)
    created_at = Column(DateTime, nullable=False, default="NOW()")
    updated_at = Column(DateTime, nullable=True)

    __table_args__ = (
        CheckConstraint("donation_amount IS NULL OR donation_amount > 0", name="chk_donation_amount_positive"),
        CheckConstraint("status IN ('PENDING', 'COMPLETED', 'EXPIRED')", name="chk_donation_status"),
    )
    
class VeterinarianSpecialty(Base):
    __tablename__ = "veterinarian_specialty"

    id = Column(UUID, primary_key=True, index=True)
    name = Column(String(50), nullable=False)

    __table_args__ = (
        CheckConstraint("name ~ '^[A-Za-zÀ-ÖØ-öø-ÿ\\s]+$'", name="chk_specialty_name_format"),
    )
    
class VeterinarianQualification(Base):
    __tablename__ = "veterinarian_qualification"

    id = Column(UUID, primary_key=True, index=True)
    name = Column(String(50), nullable=False)

    __table_args__ = (
        CheckConstraint("name ~ '^[A-Za-zÀ-ÖØ-öø-ÿ\\s]+$'", name="chk_qualification_name_format"),
    )
    
class Favorite(Base):
    __tablename__ = "favorite"

    id = Column(UUID, primary_key=True, index=True)
    veterinarian_id = Column(UUID, ForeignKey("veterinarian.id"), nullable=False)
    user_id = Column(UUID, ForeignKey("user.id"), nullable=False)

    __table_args__ = (
        UniqueConstraint("user_id", "veterinarian_id", name="uq_favorite_user_vet"),
    )

    veterinarian = relationship("Veterinarian")
    user = relationship("User")
    
    
class AvailabilityComment(Base):
    __tablename__ = "availability_comment"

    id = Column(UUID, primary_key=True, index=True)
    title = Column(String(50), nullable=False)
    description = Column(Text, nullable=False)
    veterinarian_id = Column(UUID, ForeignKey("veterinarian.id"), nullable=False)
    comment_owner_id = Column(UUID, ForeignKey("user.id"), nullable=False)

    __table_args__ = (
        CheckConstraint("title ~ '^[A-Za-zÀ-ÖØ-öø-ÿ\\s]+$'", name="chk_title_format"),
        CheckConstraint("description ~ '^[A-Za-zÀ-ÖØ-öø-ÿ\\s]+$'", name="chk_description_format"),
    )

    veterinarian = relationship("Veterinarian")
    comment_owner = relationship("User")
    


class PetPhoto(Base):
    __tablename__ = "pet_photo"

    id = Column(UUID, primary_key=True, index=True)
    photo_url = Column(Text, nullable=False)
    pet_id = Column(UUID, ForeignKey("pet.id"), nullable=False)

    __table_args__ = (
        UniqueConstraint("pet_id", "photo_url", name="uq_pet_photo_url_per_pet"),
    )

    pet = relationship("Pet")
    

class PostType(Base):
    __tablename__ = "post_type"

    id = Column(UUID, primary_key=True, index=True)
    name = Column(String(50), nullable=False)

    __table_args__ = (
        UniqueConstraint("name", name="uq_post_type_name"),
        CheckConstraint("name ~ '^[A-Za-zÀ-ÖØ-öø-ÿ\\s]+$'", name="chk_post_type_name"),
    )
    
    
class Post(Base):
    __tablename__ = "post"

    id = Column(UUID, primary_key=True, index=True)
    post_type_id = Column(UUID, ForeignKey("post_type.id"), nullable=False)
    author_id = Column(UUID, ForeignKey("user.id"), nullable=False)
    photo_url = Column(String, nullable=False)
    created_at = Column(TIMESTAMP, nullable=False, default="NOW()")
    updated_at = Column(TIMESTAMP, nullable=True)

    # Relacionamentos
    post_type = relationship("PostType", backref="posts")
    author = relationship("User", backref="posts")
    

class LostPetPost(Base):
    __tablename__ = "lost_pet_post"

    id = Column(UUID, primary_key=True, index=True)
    pet_id = Column(UUID, ForeignKey("pet.id"), nullable=False)
    location_id = Column(UUID, ForeignKey("location.id"), nullable=False)
    is_found = Column(Boolean, nullable=False)
    pet_additional_description = Column(String, nullable=True)
    reward_amount = Column(Integer, nullable=True)

    # Relacionamentos
    pet = relationship("Pet", backref="lost_pet_posts")
    location = relationship("Location", backref="lost_pet_posts")
    post = relationship("Post", backref="lost_pet_post")

    __table_args__ = (
        CheckConstraint("reward_amount IS NULL OR reward_amount >= 0", name="chk_reward_amount"),
    )
    
    
class AdoptionPetPost(Base):
    __tablename__ = "adoption_pet_post"

    post_id = Column(UUID, ForeignKey("post.id"), primary_key=True)
    pet_id = Column(UUID, ForeignKey("pet.id"), nullable=False)
    adoption_reason = Column(String, nullable=False)
    adoption_requirement = Column(String, nullable=False)

    # Relacionamentos
    post = relationship("Post", backref="adoption_pet_post")
    pet = relationship("Pet", backref="adoption_pet_post")
    

class CommunityUserPost(Base):
    __tablename__ = "community_user_post"

    id = Column(UUID, primary_key=True, index=True)
    post_subtype_id = Column(UUID, ForeignKey("post_subtype.id"), nullable=False)
    community_id = Column(UUID, ForeignKey("community_type.id"), nullable=True)
    title = Column(String(50), nullable=False)
    body = Column(Text, nullable=False)
    source_link = Column(Text, nullable=True)
    additional_link = Column(Text, nullable=True)
    up_vote_amount = Column(Integer, nullable=False, default=0)
    down_vote_amount = Column(Integer, nullable=False, default=0)
    created_at = Column(TIMESTAMP, nullable=False, default="CURRENT_TIMESTAMP")
    updated_at = Column(TIMESTAMP, nullable=True)

    # Relacionamentos
    post_subtype = relationship("PostSubtype", backref="community_user_post")
    community_type = relationship("CommunityType", backref="community_user_post")

    # Constraints
    __table_args__ = (
        CheckConstraint("title ~ '^[A-Za-zÀ-ÖØ-öø-ÿ\\s]+$'", name="chk_title_format"),
        CheckConstraint("up_vote_amount >= 0", name="chk_up_vote_non_negative"),
        CheckConstraint("down_vote_amount >= 0", name="chk_down_vote_non_negative"),
    )
    
    
class DonationPost(Base):
    __tablename__ = "donation_post"

    id = Column(UUID, primary_key=True, index=True)
    donation_id = Column(UUID, ForeignKey("donation_details.id"), nullable=False)

    # Relacionamentos
    post = relationship("Post", backref="donation_post")
    donation_details = relationship("DonationDetails", backref="donation_post")
    

class PostSubtype(Base):
    __tablename__ = "post_subtype"

    id = Column(UUID, primary_key=True, index=True)
    name = Column(String(50), nullable=False, unique=True)

    __table_args__ = (
        CheckConstraint("name ~ '^[A-Za-zÀ-ÖØ-öø-ÿ\\s]+$'", name="chk_post_subtype_name_format"),
    )
    

class CommunityType(Base):
    __tablename__ = "community_type"

    id = Column(UUID, primary_key=True, index=True)
    name = Column(String(50), nullable=False, unique=True)

    __table_args__ = (
        CheckConstraint("name ~ '^[A-Za-zÀ-ÖØ-öø-ÿ\\s]+$'", name="chk_community_type_name_format"),
    )
    

class Community(Base):
    __tablename__ = "community"

    id = Column(UUID, primary_key=True, index=True)
    community_type_id = Column(UUID, ForeignKey("community_type.id"), nullable=False)
    location_id = Column(UUID, ForeignKey("location.id"), nullable=False)
    creator_id = Column(UUID, ForeignKey("user.id"), nullable=False)
    created_at = Column(TIMESTAMP, nullable=False, default="NOW()")
    updated_at = Column(TIMESTAMP, nullable=True)

    # Relacionamentos
    community_type = relationship("CommunityType", backref="communities")
    location = relationship("Location", backref="communities")
    creator = relationship("User", backref="created_communities")

    # Constraints (se necessário)
    # __table_args__ = (
    #    CheckConstraint("community_type_id IS NOT NULL", name="chk_community_type"),
    # )
    

class BreedType(Base):
    __tablename__ = "breed_type"

    id = Column(UUID, primary_key=True, index=True)
    name = Column(String(50), nullable=False)

    # Constraint para validar o nome
    __table_args__ = (
        CheckConstraint("name ~ '^[A-Za-zÀ-ÖØ-öø-ÿ\\s]+$'", name="chk_breed_type_name"),
    )
    

class SizeType(Base):
    __tablename__ = "size_type"

    id = Column(UUID, primary_key=True, index=True)
    name = Column(String(50), nullable=False)

    # Constraints adicionais
    __table_args__ = (
        CheckConstraint("name ~ '^[A-Za-zÀ-ÖØ-öø-ÿ\\s]+$'", name="chk_size_type_name"),
    )