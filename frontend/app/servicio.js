import axios from "axios";

const URL = process.env.NEXT_PUBLIC_URL_BACK

export async function procesar(file) {
  const formData = new FormData();
  formData.append("file", file);

  try {
    const response = await axios.post(
      `${URL}/predict`,
      formData,
      {
        headers: {
          "Content-Type": "multipart/form-data",
        },
      }
    );

    return response.data;
  } catch (error) {
    console.error("Error al enviar archivo:", error);
  }
}