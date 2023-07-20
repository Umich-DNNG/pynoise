# standard imports
import unittest

# third party imports

# local imports
from lmx.ValueUnit import ValueUnit

class TestValueUnit( unittest.TestCase ) :
    """Unit test for the ValueUnit class."""

    def test_constructors( self ) :

        myValueUnit = ValueUnit( value = 7, unit = 's' )
        self.assertEqual( myValueUnit.value, 7 )
        self.assertEqual( myValueUnit.unit, 's' )

    def test_failures( self ) :

        # there is an undefined value:
        with self.assertRaises( ValueError ) :

            valueUnit = ValueUnit( value = None, unit = 's' )
            
        # there is an undefined unit:
        with self.assertRaises( ValueError ) :

            valueUnit = ValueUnit( value = 1, unit = None )
            
        # there is both an undefined value and an undefined unit:
        with self.assertRaises( ValueError ) :

            valueUnit = ValueUnit( value = None, unit = None )
            
    #Comparison:
    def test_comparison( self ) :
        
        reference = ValueUnit( value = 1, unit = 's' )
        equal = ValueUnit( value = 1, unit = 's' )
        different = ValueUnit( value = 2, unit = 'm' )
        
        self.assertTrue( reference == equal )
        self.assertFalse( reference == different )
        self.assertFalse( reference != equal )
        self.assertTrue( reference != different )

if __name__ == '__main__' :

    unittest.main()

