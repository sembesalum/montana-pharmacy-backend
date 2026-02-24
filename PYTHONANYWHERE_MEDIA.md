# Serving uploaded images on geoclimatz.pythonanywhere.com

Product (and other) images are stored in the `media/` folder and must be served at `/media/` so URLs like:

`https://geoclimatz.pythonanywhere.com/media/products/xxx.jpg`

work correctly.

## Setup on PythonAnywhere

1. Log in to [PythonAnywhere](https://www.pythonanywhere.com) and open the **Web** tab for your app.
2. Scroll to **Static files**.
3. Add a new mapping:
   - **URL:** `/media/`
   - **Directory:** `/home/geoclimatz/montana-pharmacy-backend/media`  
     (Replace `geoclimatz` with your PythonAnywhere username if different.)
4. Click **Save**.

After that, uploaded images will be available at:

`https://geoclimatz.pythonanywhere.com/media/products/...`  
`https://geoclimatz.pythonanywhere.com/media/brands/...`  
etc.

Your frontend is already set to use this domain (`NEXT_PUBLIC_API_URL` / default in `lib/api.ts`), so image URLs from the API will load correctly once this static mapping is in place.
