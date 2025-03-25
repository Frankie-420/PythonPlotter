import csv
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from typing import List, Any

# Constants for column keys and types
COLUMN_KEYS = [
    '', '"Use"', '"Layer"', '"Diam"', '"Depth"', '"x"', '"y"', '"RepQty"', '"Repx"', '"Repy"', '"z"',
    '"x2"', '"y2"', '"z2"', '"x3"', '"y3"', '"z3"', '"x4"', '"y4"', '"z4"', '"x5"', '"y5"', '"z5"',
    '"x6"', '"y6"', '"z6"', '"x7"', '"y7"', '"z7"', '"x8"', '"y8"', '"z8"', '"x9"', '"y9"', '"z9"',
    '"x10"', '"y10"', '"z10"'
]

COLUMN_TYPES = [
    'Whole Number\\String', 'Whole Number', 'String', 'Length', 'String', 'String', 'String',
    'Whole Number', 'String', 'String', '<none>', 'String', 'String', '<none>', 'String', 'String',
    '<none>', 'String', 'String', '<none>', 'String', 'String', '<none>', 'String', 'String', '<none>',
    '<none>', '<none>', '<none>', '<none>', '<none>', '<none>', '<none>', '<none>', '<none>', '<none>',
    '<none>', '<none>'
]

class BoardSize:
    """Represents the board dimensions."""
    def __init__(self, width: int = 200, height: int = 800, thickness: int = 16):
        self.width = width
        self.height = height
        self.thickness = thickness

class QltMachineRow:
    """
    Represents a row from the QLT machine TSV file.
    
    Attributes:
        use: Use field from the TSV.
        layer: Layer field.
        diam: Diameter field.
        depth: Depth field.
        x: First coordinate (as a string from TSV).
        y: Second coordinate.
        rep_qty: Repetition quantity.
        repx: Repetition x.
        repy: Repetition y.
        z: Z coordinate.
        additional_coordinates: Additional coordinate expressions, if any.
    """
    def __init__(self, use: str, layer: str, diam: str, depth: str, x: str, y: str,
                 rep_qty: str, repx: str, repy: str, z: str, *additional_coordinates: Any):
        self.coordinates = []
        self.use = use
        self.layer = layer
        self.diam = diam
        self.depth = depth
        self.coordinates.append(x) 
        self.coordinates.append(y)
        self.rep_qty = rep_qty
        self.repx = repx
        self.repy = repy
        self.coordinates.append(z)

        for coords in additional_coordinates:
          self.coordinates.append(coords)  # Additional coordinate expressions

    def calculate_coordinates(self, panel: BoardSize) -> List[List[float]]:
        """
        Calculates and groups additional coordinates into triples [x, y, z].
        
        The method replaces placeholder strings ('Dim1', 'Dim2', 'Dim3') in each coordinate expression 
        with the board's height, width, and thickness respectively, then evaluates the expression.
        """
        results = []
        current_triplet = []

      
      
        for coord_expr in self.coordinates:
            if not coord_expr:
                continue  # Skip empty strings
            print(coord_expr)
            # Replace placeholders with actual dimensions
            coord_expr = coord_expr.replace("Dim1", str(panel.height))
            coord_expr = coord_expr.replace("Dim2", str(panel.width))
            coord_expr = coord_expr.replace("Dim3", str(panel.thickness))
            
            coord_expr = coord_expr.strip('"')

            try:
                # Evaluate the expression safely. In production consider replacing eval with a proper parser.
                calculated_value = eval(coord_expr)
            except Exception as e:
                print(f"Error evaluating expression '{coord_expr}': {e}")
                continue
            
            current_triplet.append(calculated_value)
            if len(current_triplet) == 3:
                results.append(current_triplet)
                current_triplet = []
        return results

    @staticmethod
    def pack_coordinate(x: float, y: float, z: float) -> List[float]:
        """Pack coordinates into a list [x, y, z]."""
        return [x, y, z]

    def __repr__(self):
        return (f"QltMachineRow(use={self.use}, layer={self.layer}, diam={self.diam}, "
                f"depth={self.depth}, first_coordinate={self.x})")

def decode_tsv(file_path: str) -> List[List[str]]:
    """
    Decodes a TSV file into a list of rows.
    
    Each row is represented as a list of string values.
    """
    with open(file_path, mode='r', newline='', encoding='utf-8') as file:
        reader = csv.reader(file, delimiter='\t')
        data = [row for row in reader if row]  # Skip empty rows
    return data

def main():
    # Replace with your TSV file path
    file_path = 'Kick Box Rail-Drilling-100mm Band In Center 0 Sleepers-Feet.qlt'
    decoded_data = decode_tsv(file_path)
    
    qlt_rows: List[QltMachineRow] = []
    
    # Process the decoded data, skipping the first few header rows if needed
    for i, row in enumerate(decoded_data):
        if i < 4 or len(row) < 10:  # Skip header or incomplete rows
            continue
        
        try:
            # Create a QltMachineRow instance using columns starting from index 1
            qlt_row = QltMachineRow(*row[1:])
            qlt_rows.append(qlt_row)
        except Exception as e:
            print(f"Error processing row {i}: {e}")
            continue

    # Prepare the board and the plot
    board = BoardSize()
    fig, ax = plt.subplots()

    # Draw the board rectangle
    board_rect = patches.Rectangle((0, 0), board.width, board.height, linewidth=2,
                                   edgecolor='b', facecolor='none')
    ax.add_patch(board_rect)

    # Plot the calculated coordinates for each row
    for machine_row in qlt_rows:
        coordinates = machine_row.calculate_coordinates(board)
        for triplet in coordinates:
            # Assuming the triplet represents (x, y, z); here we plot (x, y)
            print(triplet)
            ax.plot(triplet[0], triplet[1], 'ro')

    # Configure the plot
    plt.title("Board Piece")
    plt.xlabel("Width")
    plt.ylabel("Height")
    plt.grid(True)
    plt.show()

if __name__ == "__main__":
    main()
