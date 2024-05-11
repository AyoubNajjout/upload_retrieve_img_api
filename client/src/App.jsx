import { useRef, useState } from 'react'
import axios from 'axios';

function App() {
  const [imgSrc, setImgSrc] = useState(null);

  const nameRef = useRef();

  const getImg = () => {
    const username = nameRef.current.value;
    axios.get(`http://127.0.0.1:8000/api/v1/auth/${username}/get-picture`, {
      responseType: 'blob'  // Specify the response type as arraybuffer
    })
    .then((res) => { // Create a Blob from the response data
      const imgUrl = URL.createObjectURL(res.data); // Convert the Blob into a URL
      setImgSrc(imgUrl); // Set the image URL as state
    })
    .catch((err) => {
      console.log(err.message);
    });
  }

  return (
    <>
      <input type="text" ref={nameRef}/>
      <button onClick={getImg}>Get Image</button>
      {imgSrc && <img src={imgSrc} alt="" />} {/* Render the image if imgSrc is available */}
    </>
  );
}

export default App;