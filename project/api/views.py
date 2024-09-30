from django.contrib.auth import authenticate, logout
from django.contrib.auth.models import User
from .models import Task 
from .serializers import TaskSerializer
from rest_framework.authtoken.models import Token
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.generics import ListAPIView

"""
UserCreateView allows for the creation of a user
"""

class UserCreateView(APIView):

    # post method to handle POST requests for creating a new user
    def post(self, request):
        # Extract data from the request body
        username = request.data.get('username')
        password = request.data.get('password')
        email = request.data.get('email')
        

        # Check if username, password, and email are provided
        if not username or not password or not email:
            return Response({'error': 'Username, password, and email are required'}, status=status.HTTP_400_BAD_REQUEST)

        # Check if a user with the same username already exists
        if User.objects.filter(username=username).exists():
            return Response({'error': 'Username already exists'}, status=status.HTTP_400_BAD_REQUEST)

        # If all data is valid, create a new user
        user = User.objects.create_user(username=username, password=password, email=email)

        # Return the created user data
        return Response(
            {
                'id': user.id,
                'username': user.username,
                'email': user.email
            },
            status=status.HTTP_201_CREATED
        )


class LoginView(APIView):

    def post(self, request):
        # Get the username and password from the request data
        username = request.data.get('username')
        password = request.data.get('password')

        # Authenticate the user
        user = authenticate(request, username=username, password=password)

        # Check if the user is authenticated successfully
        if user:

            # Get or create the user's token
            token, created = Token.objects.get_or_create(user=user)

            # Return the token in the response
            return Response(
                {'token': token.key},
                status=status.HTTP_200_OK
            )
        
        # If authentication fails, return an error response
        return Response(
            {'error': 'Invalid credentials'},
            status=status.HTTP_401_UNAUTHORIZED
        )
        
class LogoutView(APIView):
    # token-based authentication explicitly used
    authentication_classes = [TokenAuthentication] 
    # Ensure the user must be authenticated to access this view
    permission_classes = [IsAuthenticated]
    

    def post(self, request):
        # Get the header and token associated with the authenticated user
        auth_header = request.headers.get('Authorization')
        if request.user and request.user.is_authenticated:

            # Attempt to retrieve and delete the token                
            token , create = Token.objects.get_or_create(user=request.user)
            token.delete()

            # Log the user out
            logout(request)

            return Response(
                {'message': 'Successfully logged out'},
                status=status.HTTP_200_OK
            )
        elif auth_header is None:
            return Response(
                {'error': 'Authentication credentials were not provided.'},
                status=status.HTTP_401_UNAUTHORIZED
            )
        else:
            # Handle the case where an invalid or incorrect token is provided
            return Response(
                {'error': 'Invalid token'},
                status=status.HTTP_401_UNAUTHORIZED
            )
        
class TaskCreateView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        # Get the current authenticated user as the creator of the task
        creator = request.user

        # Copy the request data so we can modify it before passing to the serializer
        data = request.data.copy()
        
        # Extract executor_id if provided
        executor_id = data.get('executor')

         #creator is not the same as the executor
        if executor_id and creator.id == int(executor_id):
            return Response({'error': 'The creator of a task cannot be its executor'}, status=status.HTTP_400_BAD_REQUEST)

        # If executor_id is provided, check if the user exists, otherwise set executor to None
        if executor_id:
            try:
                executor = User.objects.get(id=executor_id)
                data['executor'] = executor.id
            except User.DoesNotExist:
                data['executor'] = None  # Set executor to None if the user does not exist
        else:
            data['executor'] = None

        # Add the creator to the data
        data['creator'] = creator.id

        # Initialize the serializer with the request data and the current context
        serializer = TaskSerializer(data=data, context={'request': request})

        # Validate the serializer and check for errors
        if serializer.is_valid():
            # Save the task to the database
            task = serializer.save(creator=creator)
            # Return the created task data with a 201 status code
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            errors = serializer.errors

            # Return validation errors if the data is invalid
            return Response(errors, status=status.HTTP_400_BAD_REQUEST)
        
class TasksCreatedByUser(APIView):
    """
    This view returns all tasks created by the authenticated user.
    """
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]  # Ensure only authenticated users can access this view

    def get(self, request):

        # Filter tasks where the creator is the current authenticated user
        tasks = Task.objects.filter(creator=request.user)
        serializer = TaskSerializer(tasks, many=True)

        # Return the serialized data as a JSON response
        return Response(serializer.data,status=status.HTTP_200_OK)
    
class TaskWithExecutorAPIView(ListAPIView):
    """
    API view to return a list of all tasks, replacing the executor with 'undefined' 
    if no executor is assigned.
    """
    queryset = Task.objects.all()  # Fetch all tasks
    serializer_class = TaskSerializer


    def list(self, request, *args, **kwargs):
        # Get the original response from ListAPIView
        response = super().list(request, *args, **kwargs)
        
        # Modify the executor field in the response if it is None
        for task in response.data:
            if task['executor'] is None:
                task['executor'] = "undefined"
        
        return Response(response.data)

class ClearDatabaseView(APIView):    
    #get method to clear data    
    def get(self, request):
        Task.objects.all().delete()
        User.objects.all().delete()
        return Response({'message': 'All data cleared successfully'}, status=200)