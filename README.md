# Gym Booking Platform

**Date:** October – December 2025 · 4th-year engineering (ING 4), Agile Management Methods (MMA) module, University of Boumerdès (UMBB)
**Team:** Adel Hettal, Abderrahmane Ferhat, Meriem Boukhedimi, Asma Hamiche

A web application for running a gym's class schedule: members book classes, coaches run their sessions, and an administrator manages accounts and the timetable. The team built it in Scrum sprints for the MMA module. It is split into three Django services that talk to each other over HTTP and a message queue. The interface is in French.

## What is in the code

**Members**
- Sign up and log in
- Browse upcoming sessions, book a place, see their bookings, cancel a booking

**Coaches**
- See the sessions they teach and who has booked each one
- Create, edit and delete their sessions

**Administrators**
- Dashboard to list, edit and delete user accounts and change roles
- List of all sessions

**Booking rules** (enforced in `reservations_service`)
- A session that has started or finished cannot be booked
- A member cannot book the same session twice
- A booking is refused when the session is full

## Architecture

| Service | Port | Responsibility |
|---|---|---|
| `auth_service` | 8001 | Custom user model with roles (MEMBER, COACH, ADMIN), registration, JWT login (Simple JWT), admin user management |
| `courses_service` | 8002 | Courses, sessions, coach assignment, capacity, home page |
| `reservations_service` | 8003 | Booking, cancellation, the rules above |

Supporting infrastructure, all in `docker-compose.yml`:
- **Traefik** (port 80) as the API gateway that routes `/api/auth`, `/api/courses`, `/api/reservations`, ...
- **Consul** (port 8500) for service registration. Each service registers itself at start-up.
- **RabbitMQ** (ports 5672, 15672). `reservations_service` publishes a message on each booking. A `notification-service` container (`auth_service` running `manage.py run_consumer`) receives it and logs it. It does not send real emails.

Each service has its own SQLite database. Pages are server-rendered Django templates. The services share one `DJANGO_SECRET_KEY`, so a JWT issued by `auth_service` is accepted by the other two.

## Stack
Python · Django 5 · Django REST Framework · Simple JWT · RabbitMQ (pika) · Consul · Traefik · Docker Compose

## Run it

Requirements: Docker with Docker Compose.

```bash
cp .env.example .env              # set DJANGO_SECRET_KEY to any long random string
docker compose up --build -d
for s in auth-service courses-service reservations-service; do
  docker compose exec $s python manage.py migrate
done
```

Create the demo accounts (`admin` / `admin123`, `coach1` / `password123`, `member1` / `password123`). These are local test credentials only:
```bash
docker compose exec auth-service python restore_users.py
```

Then open:
- http://localhost:8001/auth/login/ to log in or register
- http://localhost:8002/ for the class schedule
- http://localhost:8001/gym-admin/dashboard/ for the admin dashboard
- http://localhost:8080 for the Traefik dashboard, http://localhost:8500 for the Consul UI, http://localhost:15672 for RabbitMQ (guest / guest)

The services call each other by their Docker Compose names (`auth-service`, `courses-service`, `rabbitmq`), so running them with plain `manage.py runserver` outside Docker does not work for booking.

### Scripts
`scripts/` holds the scripts the team used to check the system by hand: seed data, end-to-end flows (`demonstrate_all.py`), RabbitMQ, Traefik and Consul checks, plus PowerShell versions. They need `pip install requests` and expect the stack to be running. Some log in as a `superadmin` user, which you create with `docker compose exec auth-service python manage.py createsuperuser`.

### Tested
On 26 Nov 2026 with Python 3.12 and Django 6.1, outside Docker: all three services pass `manage.py check` and migrate. Registration, JWT login and `/api/users/me/` work on `auth_service`. `courses_service` accepts a JWT issued by `auth_service` and creates a course. The full Docker Compose stack (booking, RabbitMQ, Traefik) has not been re-tested since the project was handed in.

### Known gaps
- The `tests.py` files are empty. There are no automated unit tests in this code.
- No CI pipeline or SonarQube configuration is included in this repository.
- `DEBUG` is on and `ALLOWED_HOSTS` is `*` by default. This is a local demo, not a deployment.

## Agile process
The module was about the process as much as the code. The team ran Scrum sprints with a backlog, sprint planning, reviews and retrospectives, and tracked the work in Jira. The sprint report is available on request.
