import kivy
kivy.require('1.9.0')

from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.button import Button
from kivy.uix.slider import Slider
from kivy.clock import Clock
from kivy.uix.togglebutton import ToggleButton
from kivy.properties import NumericProperty, ObjectProperty, BooleanProperty

import RPi.GPIO as GPIO

""" Base class for a GPIO based button """
class GPIOButton(Button):
	pin = NumericProperty(None)
	direction = NumericProperty(None)
	pull_up_down = NumericProperty(None, allownone=True)
	gpio_value = ObjectProperty(None)
	gpio_configured = BooleanProperty(False)

	def on_press(self):
		# work around widget properties not being set
		# when __init__() is called
		if not self.gpio_configured:
			if GPIO.getmode() is None:
				GPIO.setmode(GPIO.BOARD)
			print("setting up pin {}".format(self.pin))
			if self.pull_up_down is not None:
				GPIO.setup(self.pin, self.direction,
					pull_up_down=self.pull_up_down)
			else:
				GPIO.setup(self.pin, self.direction)
			if self.gpio_value is not None:
				GPIO.output(self.pin, self.gpio_value)
			self.gpio_configured = True
		return False

""" A button that changes state based on input from a GPIO pin """
class GPIOInputButton(GPIOButton):
	def __init__(self, **kwargs):
		super(GPIOInputButton, self).__init__(**kwargs)
		# Set a timer to check if the GPIO pin has changed state
		Clock.schedule_interval(self.update, 1.0/10.0)

	def update(self, dt):
		# work around widget properties not being set
		# when __init__() is called
		if not self.gpio_configured:
			if GPIO.getmode() is None:
				GPIO.setmode(GPIO.BOARD)
			print("setting up pin {}".format(self.pin))
			if self.pull_up_down is not None:
				GPIO.setup(self.pin, self.direction, pull_up_down=self.pull_up_down)
			else:
				GPIO.setup(self.pin, self.direction)
			if self.gpio_value is not None:
				GPIO.output(self.pin, self.gpio_value)
			self.gpio_configured = True

		if GPIO.input(self.pin):
			self.state = 'normal'
		else:
			self.state = 'down'

""" A button that toggles a GPIO pin when pressed """
class GPIOToggleButton(GPIOButton, ToggleButton):
	def on_press(self):
		super(GPIOToggleButton, self).on_press()
		GPIO.output(self.pin, not GPIO.input(self.pin))
		return True

""" A button that alters that state of a GPIO pin when held down """
class GPIOPressButton(GPIOButton, Button):
	PWM = None
	def on_press(self):
		super(GPIOPressButton, self).on_press()
		if (self.PWM is None) or (not self.gpio_configured):
			if GPIO.getmode() is None:
				GPIO.setmode(GPIO.BOARD)
			self.PWM = GPIO.PWM(int(self.pin), 3000)
			self.gpio_configured = True
		self.PWM.start(25)
		return True

	def on_release(self):
		self.PWM.ChangeDutyCycle(0)
		return True

""" A slider that alters the state of a GPIO pin based on current value """
class GPIOSlider(Slider):
	pin = NumericProperty(None)
	direction = NumericProperty(None)
	pull_up_down = NumericProperty(None, allownone=True)
	gpio_configured = BooleanProperty(False)
	PWM = None

	def on_value(self, instance, value):
		if (self.PWM is None) or (not self.gpio_configured):
			# work around widget properties not being set
			# when __init__() is called
			if GPIO.getmode() is None:
				GPIO.setmode(GPIO.BOARD)
			if self.pin is None:
				return True
			print("setting up pin {}".format(self.pin))

			if self.pull_up_down is not None:
				GPIO.setup(self.pin, self.direction, pull_up_down=self.pull_up_down)
			else:
				GPIO.setup(self.pin, self.direction)
			self.PWM = GPIO.PWM(int(self.pin), int(self.value))
			self.PWM.start(50)
			self.gpio_configured = True

		self.PWM.ChangeFrequency(int(self.value))
		return True

class Monitor(Widget):
	pass

class MonitorApp(App):
	def build(self):
		return Monitor()

if __name__ == '__main__':
	GPIO.setmode(GPIO.BOARD)
	MonitorApp().run()
	GPIO.cleanup()
