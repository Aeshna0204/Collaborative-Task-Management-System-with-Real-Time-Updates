# Task Management System

## Overview

This Task Management System is a web application that allows users to create, update, and manage tasks. The application includes two types of users: Admins, who can manage all tasks, and regular Users, who can only view and update their assigned tasks. The system features real-time updates using WebSockets to keep all connected users informed of any changes.

## Features

- **User Authentication:** Users can register and log in to their accounts.
- **Task Management:** 
  - Admins can create, update, and delete any tasks.
  - Users can view their tasks and update the status of their assigned tasks.
- **Real-Time Updates:** Changes made by admins are instantly reflected for assigned users via WebSockets.
- **Task Filtering:** Users can filter tasks by priority.
- **User-Specific Views:** Users can only see tasks assigned to them.

## Tech Stack

- **Backend:** FastAPI, SQLAlchemy
- **Frontend:** React.js
- **Database:** PostgreSQL
- **WebSocket:** Used for real-time communication
- **Authentication:** JSON Web Tokens (JWT)

## Installation

### Prerequisites

- Python 3.x
- PostgreSQL (or any other database you prefer)
- FastAPI

## Create a virtual environment:
```
virtualenv env
```
