# builtin
import os, sys
from typing import Optional
# 3rd party
import pytest, pydantic
# local
project_path = os.path.abspath( os.path.dirname( __file__) + "/../.." )
if not project_path in sys.path:
    sys.path.insert(0, project_path)
from nimble.data_object import DataObject

class TestModel(DataObject):
    field1: str
    field2: int
    field3: Optional[float] = pydantic.Field(default=None)

class DataObjectTest:

    def test(self):
        metadata, table = TestModel.to_sqlalchemy_table(table_name="TestModelTable")
        assert table.name == "TestModelTable"
        assert "field1" in table.columns
        assert "field2" in table.columns
        assert "field3" in table.columns
        
        instance = TestModel(id=1,field1="value1", field2=42)
        assert instance.field1 == "value1"
        assert instance.field2 == 42
        assert instance.field3 is None
        
        InsertModel = TestModel.create_insert_pydanctic_model()
        insert_instance = InsertModel(field1="value2", field2=100, field3=3.14)
        assert insert_instance.field1 == "value2"
        assert insert_instance.field2 == 100        
        assert insert_instance.field3 == 3.14
        
        UpdateModel = TestModel.create_update_model()
        update_instance = UpdateModel(field1="newvalue")
        assert update_instance.field1 == "newvalue"
        assert update_instance.field2 is None
        assert update_instance.field3 is None
        
        source = DataObject.create_source( TestModel )
        assert "class TestModel" in source
        assert "field1: str" in source
        assert "field2: int" in source
        #assert "field3: Optional[float]" in source
        path = os.path.abspath(os.path.dirname(__file__) + "/../../tmp")
        os.makedirs(path, exist_ok=True)
        fdir = os.path.join(path, "data_object_test_output.py")
        with open(fdir, "w") as f:
            print(f"Writing generated source to {fdir}")
            f.write(source)

if __name__ == "__main__":
    # Run pytest against *this* file only
    sys.exit(pytest.main([__file__, "--no-cov"]))