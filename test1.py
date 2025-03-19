import tkinter as tk
from tkinter import ttk, messagebox
import requests
from datetime import datetime

class WeatherApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Weather Wizard")
        self.root.geometry("800x600")
        self.api_key = "4737b340e76af2514de6916025283eae" 
        self.base_url = "http://api.openweathermap.org/data/2.5/weather"
        self.forecast_url = "http://api.openweathermap.org/data/2.5/forecast"
        self.icon_url = "https://openweathermap.org/img/wn/{}@2x.png"
        
        # Configure styles
        self.style = ttk.Style()
        self.style.configure('TFrame', background='#e0e0e0')
        self.style.configure('TLabel', background='#e0e0e0', font=('Arial', 10))
        self.style.configure('Header.TLabel', font=('Arial', 14, 'bold'))
        
        self.create_widgets()
        
    def create_widgets(self):
        # Input Frame
        input_frame = ttk.Frame(self.root, padding=10)
        input_frame.pack(fill=tk.X)
        
        self.location_entry = ttk.Entry(input_frame, width=30, font=('Arial', 12))
        self.location_entry.pack(side=tk.LEFT, padx=5)
        self.location_entry.bind('<Return>', lambda e: self.get_weather())
        
        ttk.Button(input_frame, text="Get Weather", command=self.get_weather).pack(side=tk.LEFT, padx=5)
        ttk.Button(input_frame, text="Use My Location", command=self.get_current_location).pack(side=tk.LEFT, padx=5)
        
        # Current Weather Frame
        self.current_frame = ttk.Frame(self.root, padding=20)
        self.current_frame.pack(fill=tk.X, pady=10)
        
        # Weather Icon
        self.icon_label = ttk.Label(self.current_frame)
        self.icon_label.grid(row=0, column=0, rowspan=3, padx=10)
        
        # Weather Details
        self.location_label = ttk.Label(self.current_frame, style='Header.TLabel')
        self.location_label.grid(row=0, column=1, sticky=tk.W)
        
        self.temp_label = ttk.Label(self.current_frame, style='Header.TLabel')
        self.temp_label.grid(row=1, column=1, sticky=tk.W)
        
        self.details_label = ttk.Label(self.current_frame)
        self.details_label.grid(row=2, column=1, sticky=tk.W)
        
        # Forecast Frame
        forecast_frame = ttk.Frame(self.root)
        forecast_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        ttk.Label(forecast_frame, text="5-Day Forecast", style='Header.TLabel').pack(anchor=tk.W)
        
        self.forecast_container = ttk.Frame(forecast_frame)
        self.forecast_container.pack(fill=tk.BOTH, expand=True)
        
    def get_weather(self):
        location = self.location_entry.get()
        if not location:
            messagebox.showwarning("Warning", "Please enter a location")
            return
            
        try:
            # First get coordinates for the location
            geo_params = {
                'q': location,
                'appid': self.api_key
            }
            response = requests.get("http://api.openweathermap.org/geo/1.0/direct", params=geo_params)
            response.raise_for_status()
            geo_data = response.json()
            
            if not geo_data:
                messagebox.showerror("Error", "Location not found")
                return
                
            lat = geo_data[0]['lat']
            lon = geo_data[0]['lon']
            self.update_weather(lat, lon)
            self.update_forecast(lat, lon)
            
        except Exception as e:
            messagebox.showerror("Error", str(e))
    
    def get_current_location(self):
        try:
            # Get approximate location using IP geolocation
            response = requests.get("https://freegeoip.app/json/")
            response.raise_for_status()
            geo_data = response.json()
            self.location_entry.delete(0, tk.END)
            self.location_entry.insert(0, f"{geo_data['city']}, {geo_data['country_code']}")
            self.update_weather(geo_data['latitude'], geo_data['longitude'])
            self.update_forecast(geo_data['latitude'], geo_data['longitude'])
            
        except Exception as e:
            messagebox.showerror("Error", f"Could not get location: {str(e)}")
    
    def update_weather(self, lat, lon):
        try:
            params = {
                'lat': lat,
                'lon': lon,
                'appid': self.api_key,
                'units': 'metric'
            }
            response = requests.get(self.base_url, params=params)
            response.raise_for_status()
            data = response.json()
            
            # Update display
            self.location_label.config(text=data['name'])
            self.temp_label.config(text=f"{data['main']['temp']:.1f}°C")
            weather_desc = data['weather'][0]['description'].title()
            details = (f"Humidity: {data['main']['humidity']}%\n"
                       f"Wind: {data['wind']['speed']} m/s\n"
                       f"Conditions: {weather_desc}")
            self.details_label.config(text=details)
            
            # Update icon
            icon_code = data['weather'][0]['icon']
            self.display_weather_icon(icon_code)
            
        except Exception as e:
            messagebox.showerror("Error", str(e))
    
    def update_forecast(self, lat, lon):
        try:
            params = {
                'lat': lat,
                'lon': lon,
                'appid': self.api_key,
                'units': 'metric'
            }
            response = requests.get(self.forecast_url, params=params)
            response.raise_for_status()
            data = response.json()
            
            # Clear previous forecast
            for widget in self.forecast_container.winfo_children():
                widget.destroy()
            
            # Display 5-day forecast (3-hour increments, taking daily at 12:00)
            for i in range(0, 40, 8):
                forecast = data['list'][i]
                date = datetime.fromtimestamp(forecast['dt']).strftime('%a, %b %d')
                temp = forecast['main']['temp']
                icon_code = forecast['weather'][0]['icon']
                desc = forecast['weather'][0]['description'].title()
                
                frame = ttk.Frame(self.forecast_container, padding=10, relief=tk.RIDGE)
                frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
                
                ttk.Label(frame, text=date, font=('Arial', 10, 'bold')).pack()
                self.display_weather_icon(icon_code, frame, scale=0.8)
                ttk.Label(frame, text=f"{temp:.1f}°C").pack()
                ttk.Label(frame, text=desc, wraplength=100).pack()
                
        except Exception as e:
            messagebox.showerror("Error", str(e))
    
    def display_weather_icon(self, icon_code, parent=None, scale=1.0):
        if not parent:
            parent = self.icon_label
            
        try:
            response = requests.get(self.icon_url.format(icon_code), stream=True)
            img = tk.PhotoImage(data=response.content)
            img = img.subsample(int(2/scale), int(2/scale))  # Scale image
            if parent == self.icon_label:
                parent.config(image=img)
                parent.image = img
            else:
                label = ttk.Label(parent, image=img)
                label.image = img
                label.pack()
        except:
            # Fallback if icon can't be loaded
            pass

if __name__ == "__main__":
    root = tk.Tk()
    app = WeatherApp(root)
    root.mainloop()