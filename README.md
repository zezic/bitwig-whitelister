# Bitwig Whitelister

Tool to allow using 3rd party native devices and modulators in Bitwig

## Usage

**python3 whitelist.py** [**--modulator** "UUID:Name"] [**--device** "UUID:Name"] **--jar** bitwig.jar **--output** bitwig-patched.jar

Where UUID is UUID of your modulator or device and Name is it's name. You can use multiple `--modulator/--device` arguments.

## Example

```bash
python3 whitelist.py --modulator "7146bcd7-f813-44c6-96e5-2e9d77093a81:Zath" --jar bitwig.jar --output bitwig-patched.jar
```
