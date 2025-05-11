import numpy as np
from photompy import * 
from scipy.interpolate import RegularGridInterpolator
import os


class IESData:
    def __init__(self, data_dict=None, ies_file_path=None):
        if data_dict is not None:
            self.photometric_data = data_dict
            self.angles = {
                'vertical': data_dict['thetas'],
                'horizontal': data_dict['phis']
            }
            self.candela_values = data_dict['values']
        elif ies_file_path is not None:
            self.ies_file_path = ies_file_path
            self.photometric_data = None
            self.angles = None
            self.candela_values = None
            self.parse_ies_file()
        else:
            raise ValueError("Either data_dict or ies_file_path must be provided")


class IrradianceCalculator:
    def __init__(self, ies_data, room_width, room_length, mounting_height):
        self.ies_data = ies_data
        self.room_width = room_width
        self.room_length = room_length
        self.mounting_height = mounting_height
        
        # Create interpolation function for candela values
        self.interpolator = RegularGridInterpolator(
            (ies_data.angles['horizontal'], ies_data.angles['vertical']),
            ies_data.candela_values,
            method='linear',
            bounds_error=False,
            fill_value=0
        )


    def calculate_irradiance_at_point(self, x, y, z):
        """Calculate irradiance at a specific point in the room."""
        # Calculate distance and angles
        dx = x - self.room_width/2
        dy = y - self.room_length/2
        dz = z - self.mounting_height
        
        distance = np.sqrt(dx**2 + dy**2 + dz**2)
        if distance == 0:
            return 0

        # Calculate angles in degrees
        # For vertical angle (theta), we want 0 at the top and 90 at the horizontal
        print(f"dx: {dx}, dy: {dy}, dz: {dz}")
        theta = np.degrees(np.arctan2(np.sqrt(dx**2 + dy**2), np.abs(dz))) # Vertical angle
        if theta < 0:
            theta += 180
            
        # For horizontal angle (phi), we want 0 at the front and increasing clockwise
        phi = np.degrees(np.arctan2(dy, dx))  # Horizontal angle
        if phi < 0:
            phi += 360
            
        print(f"phi: {phi}, theta: {theta}")
        # Get candela value through interpolation
        candela = self.interpolator((phi, theta))
        
        # Calculate irradiance using inverse square law
        theta_rad = np.radians(theta)
        irradiance = candela * np.cos(theta_rad) / (distance**2)
        return irradiance

    def calculate_average_irradiance(self, target_height, grid_size=0.05):
        """Calculate average irradiance at a specific height."""
        x_points = np.arange(0, self.room_width + grid_size, grid_size)
        y_points = np.arange(0, self.room_length + grid_size, grid_size)
        
        total_irradiance = 0
        count = 0
        
        for x in x_points:
            for y in y_points:
                print(f"x: {x}, y: {y}")
                irradiance = self.calculate_irradiance_at_point(x, y, target_height)
                total_irradiance += irradiance
                count += 1
                
        return total_irradiance / count if count > 0 else 0
    
    def calculate_maximum_irradiance(self, target_height, grid_size=0.05):
        """Calculate maximum irradiance in the room."""
        x_points = np.arange(0, self.room_width, grid_size)
        y_points = np.arange(0, self.room_length, grid_size)
        
        max_irradiance = 0  
        for x in x_points:
            for y in y_points:
                irradiance = self.calculate_irradiance_at_point(x, y, target_height)
                if irradiance > max_irradiance:
                    max_irradiance = irradiance
        return max_irradiance
    

def main():
    try:
        lampdict = read_ies_data('USHIO_B1_(PRERELEASE_DATA).ies')
        ies_data = lampdict['interp_vals']

        # Room dimensions and mounting height
        room_width = 3.36 # meters
        room_length = 4.2  # meters
        mounting_height = 2.26 # meters
        target_height = 1.8  # meters
        
        # Create IES data object
        ies = IESData(data_dict=ies_data)
        
        # Create calculator
        calculator = IrradianceCalculator(
            ies,
            room_width,
            room_length,
            mounting_height
        )
        
        # Calculate average irradiance
        avg_irradiance = calculator.calculate_average_irradiance(target_height)
        max_irradiance = calculator.calculate_maximum_irradiance(target_height)
        
        print(f"\nResults:")
        print(f"Average irradiance at {target_height}m height: {(0.1 * avg_irradiance):.3f} W/cm²")
        print(f"Maximum irradiance at {target_height}m height: {(0.1 * max_irradiance):.3f} W/cm²")
        
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    main() 