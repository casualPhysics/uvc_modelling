import numpy as np
import matplotlib.pyplot as plt
import math

class IESVisualizer:
    def __init__(self, ies_file_path):
        self.ies_file_path = ies_file_path
        self.angles = None
        self.candela_values = None
        self.parse_ies_file()

    def parse_ies_file(self):
        """Parse the IES file to extract angles and candela values."""
        with open(self.ies_file_path, 'r') as f:
            content = f.read()

        # Find the data section
        if '[DISTRIBUTION]' in content:
            data_section = content.split('[DISTRIBUTION]')[1]
        else:
            data_section = content

        # Extract numbers
        numbers = [float(x) for x in data_section.split() if x.strip() and x.strip().upper() not in ['=NONE', 'NONE']]

        # First number is number of vertical angles
        num_vertical = int(numbers[0])
        numbers = numbers[1:]

        # Next num_vertical numbers are vertical angles
        vertical_angles = np.array(numbers[:num_vertical])
        numbers = numbers[num_vertical:]

        # Next number is number of horizontal angles
        num_horizontal = int(numbers[0])
        numbers = numbers[1:]

        # Next num_horizontal numbers are horizontal angles
        horizontal_angles = np.array(numbers[:num_horizontal])
        numbers = numbers[num_horizontal:]

        # Remaining numbers are candela values
        candela_values = np.array(numbers[:num_horizontal * num_vertical]).reshape(num_horizontal, num_vertical)

        self.angles = {
            'vertical': vertical_angles,
            'horizontal': horizontal_angles
        }
        self.candela_values = candela_values

    def render(self, size=512, horizontal_angle=0.0, distance=0.0, blur_radius=1.0, save=True, out_path=None):
        """Render the IES data as an image using matplotlib."""
        # Create a figure with a black background
        plt.figure(figsize=(10, 10), facecolor='black')
        
        # Create a polar plot
        ax = plt.subplot(111, projection='polar')
        ax.set_facecolor('black')
        
        # Create meshgrid for angles
        theta = np.radians(self.angles['horizontal'])
        r = self.angles['vertical']
        theta, r = np.meshgrid(theta, r)
        
        # Plot the candela values
        im = ax.pcolormesh(theta, r, self.candela_values.T, 
                          cmap='hot', shading='auto')
        
        # Customize the plot
        ax.set_title('IES Light Distribution', color='white', pad=20)
        ax.grid(True, color='gray', alpha=0.3)
        
        # Add colorbar
        cbar = plt.colorbar(im)
        cbar.set_label('Candela', color='white')
        cbar.ax.yaxis.label.set_color('white')
        cbar.ax.tick_params(colors='white')
        
        # Set the radial axis to show angles from 0 to 90 degrees
        ax.set_rlim(0, 90)
        
        # Save the image if requested
        if save:
            if out_path is None:
                import os
                os.makedirs('visualizations', exist_ok=True)
                base_name = os.path.splitext(os.path.basename(self.ies_file_path))[0]
                out_path = f'visualizations/{base_name}_visualization.png'
            
            plt.savefig(out_path, 
                       facecolor='black',
                       edgecolor='none',
                       bbox_inches='tight',
                       pad_inches=0.5)
            print(f"Visualization saved to: {out_path}")
        
        plt.close()
        return out_path 