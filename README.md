# CropIrrigator - Smart Farming Assistant

A Kivy-based mobile application that provides personalized irrigation advice based on crop type, weather conditions, and soil moisture data.

## Features

- **User Authentication**: Secure login and signup system with email validation
- **Location Services**: GPS and manual location input with map visualization
- **Crop Selection**: Choose from various vegetables and growth stages
- **Weather Integration**: Real-time weather data from OpenWeatherMap API
- **Data Visualization**: Weather charts showing temperature and rainfall patterns
- **Database Storage**: SQLite database for user data, locations, and crop selections

## Installation

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd CropIrrigator
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Install additional Kivy Garden packages**:
   ```bash
   pip install kivy-garden
   garden install mapview
   ```

## Dependencies

- **Kivy 2.2.1**: Main GUI framework
- **KivyMD 1.1.1**: Material Design components
- **Requests 2.28.2+**: HTTP requests for weather API
- **Geopy 2.3.0+**: Geocoding and location services
- **Matplotlib 3.5.0+**: Data visualization
- **Plyer 2.1.0+**: Platform-specific features (GPS)

## Project Structure

```
CropIrrigator/
├── main.py                 # Main application entry point
├── user_db.py             # User authentication and database
├── location_db.py         # Location storage and management
├── vegetable_db.py        # Crop selection database
├── weather_data.py        # Weather API integration
├── requirements.txt       # Python dependencies
├── README.md             # Project documentation
├── assets/               # Images and static files
│   ├── welcomeimage.png
│   └── icon1.png
└── *.kv                  # Kivy UI definition files
    ├── welcome.kv
    ├── login.kv
    ├── signup.kv
    ├── home.kv
    ├── location.kv
    ├── vegetable_selection.kv
    └── weather_chart.kv
```

## Usage

1. **Run the application**:
   ```bash
   python3 main.py
   ```

2. **Application Flow**:
   - Welcome screen with login/signup options
   - User authentication
   - Home screen with navigation options
   - Location setup (GPS or manual search)
   - Vegetable and growth stage selection
   - Weather data visualization

## Database Schema

### Users Table
- `id`: Primary key
- `email`: Unique user email
- `password_hash`: Hashed password

### Locations Table
- `id`: Primary key
- `method`: GPS or manual
- `latitude`: Location latitude
- `longitude`: Location longitude
- `timestamp`: Creation timestamp

### Vegetable Selections Table
- `id`: Primary key
- `vegetable`: Selected crop type
- `growthStage`: Growth stage
- `timestamp`: Selection timestamp

### Weather History Table
- `id`: Primary key
- `date`: Weather date
- `temperature`: Average temperature
- `rain`: Total rainfall
- `soil_moisture`: Soil moisture data

## API Configuration

The application uses OpenWeatherMap API for weather data. The API key is configured in `weather_data.py`. For production use, consider using environment variables for API keys.

## Troubleshooting

### Common Issues

1. **Import Errors**: Ensure all dependencies are installed
2. **GPS Issues**: Check device permissions for location access
3. **Weather API Errors**: Verify API key and internet connection
4. **Database Errors**: Check file permissions for database creation

### Debug Mode

Run with verbose logging:
```bash
python3 main.py --debug
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support and questions, please open an issue on the project repository.
