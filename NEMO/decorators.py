import inspect
from threading import Lock, RLock, Thread

from django.contrib.auth import REDIRECT_FIELD_NAME
from django.contrib.auth.decorators import user_passes_test
from django.utils.text import slugify


def disable_session_expiry_refresh(f):
	"""
	Security policy dictates that the user's session should time out after a set duration.
	The user's session is automatically refreshed (that is, the expiration date
	of their session is moved forward to 30 minutes after the request time) whenever
	the user performs an action. Pages such as the Calendar, Tool Control, and Status Dashboard
	all have polling AJAX requests to update information on the page. These regular polling
	requests should not refresh the session (because it does not indicate the user took
	an action). Place this decorator on any view that is regularly polled so that the
	user's session is not refreshed.
	"""
	f.disable_session_expiry_refresh = True
	return f


# Use this decorator on a function to make a call to said function asynchronous
# The function will be run in a separate thread, and the current execution will continue
def postpone(function):
	def decorator(*arguments, **named_arguments):
		t = Thread(target=function, args=arguments, kwargs=named_arguments)
		t.daemon = True
		t.start()

	return decorator


# Use this decorator annotation to prevent concurrent execution of a function
# Passing a method argument will only lock a function being called with that same argument
# For example, @synchronized('tool_id') on a do_this(tool_id) function will only prevent do_this from being called
# at the same time with the same tool_id. If do_this is called twice with different tool_id, it won't be locked
def synchronized(method_argument=""):
	def inner(function):
		def decorator(*args, **kwargs):
			func_args = inspect.signature(function).bind(*args, **kwargs).arguments
			attribute_value = slugify(str(func_args.get(method_argument, ""))).replace("-", "_")
			lock_name = "__" + function.__name__ + "_lock_" + attribute_value + "__"
			lock: RLock = vars(function).get(lock_name, None)
			if lock is None:
				meta_lock = vars(decorator).setdefault("_synchronized_meta_lock", Lock())
				with meta_lock:
					lock = vars(function).get(lock_name, None)
					if lock is None:
						lock = RLock()
						setattr(function, lock_name, lock)
			with lock:
				return function(*args, **kwargs)

		return decorator

	return inner


def staff_member_required(view_func=None, redirect_field_name=REDIRECT_FIELD_NAME, login_url=None):
	"""
	Decorator for views that checks that the user is logged in and is a staff member.
	"""
	actual_decorator = user_passes_test(
		lambda u: u.is_active and u.is_staff, login_url=login_url, redirect_field_name=redirect_field_name
	)
	if view_func:
		return actual_decorator(view_func)
	return actual_decorator


def superuser_required(view_func=None, redirect_field_name=REDIRECT_FIELD_NAME, login_url=None):
	"""
	Decorator for views that checks that the user is logged in and is a superuser.
	"""
	actual_decorator = user_passes_test(
		lambda u: u.is_active and u.is_superuser, login_url=login_url, redirect_field_name=redirect_field_name
	)
	if view_func:
		return actual_decorator(view_func)
	return actual_decorator


def staff_member_or_tool_superuser_required(view_func=None, redirect_field_name=REDIRECT_FIELD_NAME, login_url=None):
	"""
	Decorator for views that checks that the user is logged in and is either a staff member or a superuser
	on a tool (any tool).
	"""
	actual_decorator = user_passes_test(
		lambda u: u.is_active and (u.is_staff or u.is_tool_superuser),
		login_url=login_url,
		redirect_field_name=redirect_field_name,
	)
	if view_func:
		return actual_decorator(view_func)
	return actual_decorator
