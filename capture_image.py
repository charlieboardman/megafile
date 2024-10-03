import cv2
import img2pdf

def capture_image():
    n = 0
    # Initialize the webcam
    cap = cv2.VideoCapture(0)
    
    # Adding this mysterious line fixes the resolution issue and allows me to actually set it
    # https://github.com/opencv/opencv/issues/24289
    cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter.fourcc('M', 'J', 'P', 'G')) 
    
    cap.set(3, 2048)
    cap.set(4, 2048)
    
    print("Set Resolution:", cap.get(cv2.CAP_PROP_FRAME_WIDTH), cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    print("Press 'Space' to capture a page, 'Enter' to finish capturing, or 'Esc' to quit without saving.")
    
    pages = []  # List to store the pages of a multi-page capture

    while True:
        # Capture frame-by-frame
        ret, frame = cap.read()
        
        # Crop the frame to 8.5/11 aspect ratio
        height, width = frame.shape[:2]
        target_ratio = 8.5 / 11
        current_ratio = width / height
        
        if current_ratio > target_ratio:
            # Width needs to be reduced
            new_width = int(height * target_ratio)
            start = (width - new_width) // 2
            frame = frame[:, start:start+new_width]
        else:
            # Height needs to be reduced
            new_height = int(width / target_ratio)
            start = (height - new_height) // 2
            frame = frame[start:start+new_height, :]
        
        # Scale down the frame for display
        display_frame = cv2.resize(frame, (0, 0), fx=0.5, fy=0.5)
        
        # Display the resulting frame
        cv2.imshow('Live Feed', display_frame)
        
        # Wait for a key press
        key = cv2.waitKey(1) & 0xFF
        
        if key == 27:  # 27 is the ASCII code for Escape key
            print("Capture process cancelled. No files saved.")
            cap.release()
            cv2.destroyAllWindows()
            return None, None
        
        if key == ord(' '):  # Capture a sequence of images with space
            pages.append(frame.copy())  # Save the full resolution frame
            n += 1
            print(f'Page {n} captured')
            continue
        
        if key == 13:  # 13 is enter
            if not pages:  # If no pages were captured
                print("No pages captured. Exiting without saving.")
                cap.release()
                cv2.destroyAllWindows()
                return None, None
            pages.append(frame.copy())  # Save the full resolution frame
            n += 1
            print(f'{n} page(s) captured')
            break  # Exit the loop

    # When everything is done, release the capture and close windows
    cap.release()
    cv2.destroyAllWindows()

    # Convert the list of images to a list of PNG bytes arrays
    image_bytes = [cv2.imencode('.png', page)[1].tobytes() for page in pages]
    
    # Convert the list of bytes arrays to a PDF
    pdf_bytes = img2pdf.convert(image_bytes)
    
    return pdf_bytes