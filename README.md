# Smart Message Language (SML) Decoder
## Receiving from SMART METER 

* Take a USB / UART converter
* Put a phototransistor ca. (750nm - 1100nm) 
* C - GND, E - DATA + 3,3kOhm Pullup to 5V
* 9600 Baud 8N1

## Decode SML 
### Frame

| Packet | Data |
|--- | ---:|
| Start | 0x1B1B1B1B |
| Version | 0x01010101 |
| Data block | .... |
| Fill bytes | 0x00.. |
| Escape | 0x1B1B1B1B |
| End    | 0x1A |
| Number of fill bytes | 0x0x |
| CRC16 | 0xXXXX |

### Data Block
| Type | Code |
|--- | ---:|
|List | 0x70 |
|Unsigned | 0x60 |
|Integer | 0x50 |
|Boolean | 0x40 |
|String | 0x70 |
|Ext string | 0x8000 |
|Other | 0xC000 |
