import numpy as np
import cv2 as cv
import sacn

# provide an IP-Address to bind to if you are using Windows and want to use multicast
sender = sacn.sACNsender()
sender.start()  # start the sending thread

sender.activate_output(1)  # start sending out data in the 1st universe
sender[1].multicast = False  # set multicast to True
sender[1].destination = '192.168.123.142'

sender.activate_output(2)  # start sending out data in the 1st universe
sender[2].multicast = False  # set multicast to True
sender[2].destination = '192.168.123.142'

cap = cv.VideoCapture('test.flv')
while cap.isOpened():
    ret, frame = cap.read()
    # if frame is read correctly ret is True
    if not ret:
        print("Can't receive frame (stream end?). Exiting ...")
        break
    # height, width, channels = frame.shape
    blue = int(frame[100, 100, 0])  # B Channel Value
    green = int(frame[100, 100, 1])  # G Channel Value
    red = int(frame[100, 100, 2])  # R Channel Value

    print(frame[100, 100])
    print(frame[100, 100, 0])

    sender[1].dmx_data = (blue, green, red) * 170
    sender[2].dmx_data = (blue, green, red) * 170

    cv.imshow('frame', frame)
    if cv.waitKey(100) == ord('q'):
        break

sender.stop()
cap.release()
cv.destroyAllWindows()


def transform(frames):
    items = []
    for idx, frame in frames:
        items.append(frame)
        if(idx % 10 == 9):
            # 每10个像素，再反向添加一次。比如像素1到10，处理后的数组为[1...10,10,9,8...1]的20个元素的新数组
            for x in range(10):
                items.append(frames[idx-x])

    assert len(items) == 2 * len(frames)
    return items


def toDmx(frames):
    # 每个输出模块包含300个LED, 900个Channel。这些channel被分配到两个universe
    outputs = []

    for idx, frame in frames:
        if idx % 50 == 0:
            outputs.append(())

        blue = int(frame[0])  # B Channel Value
        green = int(frame[1])  # G Channel Value
        red = int(frame[2])  # R Channel Value

        outputs[-1] += (blue,green,red) * 6

    assert len(outputs[-1]) == 900

    universes = []
    for output in outputs:
        universes.append(output[:510:])
        universes.append(output[510::])
