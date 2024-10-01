# get_job_titles.py

class JobTitleExtractor:
    def __init__(self, client):
        self.client = client

    def get_job_titles(self, user_input):
        if user_input:
            template_string = """
            You are an expert in job title identification. Your task is to provide a comma-separated list of job titles that are directly relevant to the given LinkedIn post.

            **LinkedIn Post:**
            {context}

            **Instructions:**
            - Analyze the content of the LinkedIn post.
            - Extract only the job titles that are mentioned or implied based on the content.
            - Provide the job titles in a comma-separated list format, without additional explanations or descriptions.
            - If no job titles are relevant, respond with 'No relevant job titles found.'

            **Job Titles:**
            """
            
            prompt = template_string.format(context=user_input)

            try:
                response = self.client.chat.completions.create(
                    model="llama3-8b-8192",
                    messages=[
                        {"role": "system", "content": "You are an expert in job title identification. Only list the job titles based on the content of the LinkedIn post, separated by commas. No additional information is needed."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.0
                )
                job_titles = response.choices[0].message.content.strip()
                return job_titles

            except Exception as e:
                raise Exception(f"Failed to extract job titles: {e}")
        else:
            raise ValueError("Input Required: Please enter LinkedIn post content.")
