# MetaMorph
A flexible, graph-based file format converter for the command line.

## 🌟 Overview  
MetaMorph is a command-line tool that intelligently converts files between different formats. It leverages graph search to find the most efficient conversion path, allowing for batch processing, multi-format handling, and user-defined extensions.

## 🔧 Installation  
Clone the repository and install dependencies:  
```bash
git clone https://github.com/armindoflores/metamorph.git
cd metamorph
pip install -r requirements.txt
```

## 🚀 Usage
### Basic Conversion
Convert a file from one format to another:

```bash
mm input.png output.pdf
```

## 🔍 Features (Planned)
- [ ] Smart conversion pathfinding using graph search
- [ ] Batch processing (ext[] → ext)
- [ ] Multi-output support (ext → {ext1, ext2})
- [ ] Extensible: Define custom conversion rules
- [ ] Plugin system for additional format support

## 📜 License
MIT License. Feel free to modify and contribute!
